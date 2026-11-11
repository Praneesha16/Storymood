"""Create the StoryMood sign-in (Amazon Cognito) in one go. Run once, from the backend folder:

    python scripts/setup_cognito.py --app-url http://localhost:3000 --prefix storymood-<yourname>

Needs valid AWS credentials in .env (or the AWS CLI profile). What it creates:
  * a user pool on the Essentials tier: email + password accounts (created and activated by our API,
    so no email code at sign-up); email is the username;
    Cognito emails only password-reset codes
  * an app client without a secret, authorization-code flow with PKCE, 1-hour tokens
  * a Managed Login domain and a branding style, so Cognito hosts the sign-in pages
It prints the four values to paste into .env. Google sign-in is added afterwards in the console
(User pool -> Social providers -> Google) with a Google OAuth client id; nothing here changes.
"""
import argparse
import os
import sys

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--app-url", required=True, help="where the app runs, e.g. http://localhost:3000 or https://stories.example.com")
    ap.add_argument("--prefix", required=True, help="globally unique domain prefix, lowercase letters and dashes")
    ap.add_argument("--region", default=os.getenv("AWS_REGION", "us-east-1"))
    args = ap.parse_args()
    idp = boto3.client("cognito-idp", region_name=args.region)

    pool = idp.create_user_pool(
        PoolName="storymood-families",
        UserPoolTier="ESSENTIALS",
        UsernameAttributes=["email"],
        Policies={
            "PasswordPolicy": {"MinimumLength": 8, "RequireUppercase": True, "RequireLowercase": True, "RequireNumbers": True, "RequireSymbols": False},
            "SignInPolicy": {"AllowedFirstAuthFactors": ["PASSWORD"]},
        },
        AdminCreateUserConfig={"AllowAdminCreateUserOnly": False},
        AccountRecoverySetting={"RecoveryMechanisms": [{"Priority": 1, "Name": "verified_email"}]},
        UserAttributeUpdateSettings={"AttributesRequireVerificationBeforeUpdate": ["email"]},
        DeletionProtection="ACTIVE",
        Schema=[
            {"Name": "email", "AttributeDataType": "String", "Required": True, "Mutable": True},
            {"Name": "name", "AttributeDataType": "String", "Required": False, "Mutable": True},
        ],
    )["UserPool"]
    pool_id = pool["Id"]
    print("user pool:", pool_id)

    client = idp.create_user_pool_client(
        UserPoolId=pool_id,
        ClientName="storymood-web",
        GenerateSecret=False,
        ExplicitAuthFlows=["ALLOW_USER_AUTH", "ALLOW_REFRESH_TOKEN_AUTH"],
        SupportedIdentityProviders=["COGNITO"],
        CallbackURLs=[args.app_url + "/"],
        LogoutURLs=[args.app_url + "/"],
        AllowedOAuthFlows=["code"],
        AllowedOAuthScopes=["openid", "email", "profile"],
        AllowedOAuthFlowsUserPoolClient=True,
        PreventUserExistenceErrors="ENABLED",
        EnableTokenRevocation=True,
        AccessTokenValidity=1, IdTokenValidity=1, RefreshTokenValidity=30,
        TokenValidityUnits={"AccessToken": "hours", "IdToken": "hours", "RefreshToken": "days"},
    )["UserPoolClient"]
    print("app client:", client["ClientId"])

    try:
        idp.create_user_pool_domain(Domain=args.prefix, UserPoolId=pool_id, ManagedLoginVersion=2)
    except ClientError as exc:
        print("domain:", exc, file=sys.stderr)
        return 1
    domain = f"{args.prefix}.auth.{args.region}.amazoncognito.com"
    print("domain:", domain)
    try:
        idp.create_managed_login_branding(UserPoolId=pool_id, ClientId=client["ClientId"], UseCognitoProvidedValues=True)
    except ClientError as exc:
        print("branding (optional):", exc, file=sys.stderr)

    print("\nPaste into backend/.env:\n")
    print("AUTH_MODE=cognito")
    print(f"COGNITO_REGION={args.region}")
    print(f"COGNITO_USER_POOL_ID={pool_id}")
    print(f"COGNITO_CLIENT_ID={client['ClientId']}")
    print(f"COGNITO_DOMAIN={domain}")
    print(f"ALLOWED_ORIGINS={args.app_url}")
    print("\nAnd into frontend/.env:\n")
    print("REACT_APP_AUTH_MODE=cognito")
    return 0


if __name__ == "__main__":
    sys.exit(main())

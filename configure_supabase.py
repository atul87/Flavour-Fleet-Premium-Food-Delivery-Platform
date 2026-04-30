#!/usr/bin/env python3
"""
Supabase Configuration Helper for Flavour Fleet
Helps users easily set up Supabase credentials
"""

import os
import sys
from pathlib import Path


def get_env_file():
    """Get path to .env file"""
    backend_dir = Path(__file__).parent / "backend"
    return backend_dir / ".env"


def read_env_file(env_path):
    """Read existing .env file"""
    env_data = {}
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_data[key.strip()] = value.strip()
    return env_data


def write_env_file(env_path, env_data):
    """Write .env file"""
    with open(env_path, "w") as f:
        f.write("# ============================================\n")
        f.write("# FLAVOUR FLEET — Environment Configuration\n")
        f.write("# ============================================\n\n")

        f.write("# ─── Database ──────────────────────────────\n")
        f.write(
            f'MONGODB_URI={env_data.get("MONGODB_URI", "mongodb://localhost:27017/flavourfleet")}\n\n'
        )

        f.write("# ─── Supabase Authentication ────────────────\n")
        f.write(
            f'SUPABASE_URL={env_data.get("SUPABASE_URL", "https://YOUR_PROJECT_ID.supabase.co")}\n'
        )
        f.write(
            f'SUPABASE_SERVICE_KEY={env_data.get("SUPABASE_SERVICE_KEY", "YOUR_SERVICE_KEY")}\n\n'
        )

        f.write("# ─── Email Service (Optional) ──────────────\n")
        f.write(
            f'RESEND_API_KEY={env_data.get("RESEND_API_KEY", "your_resend_api_key")}\n\n'
        )

        f.write("# ─── Server Configuration ──────────────────\n")
        f.write(f'FLASK_ENV={env_data.get("FLASK_ENV", "development")}\n')
        f.write(
            f'SECRET_KEY={env_data.get("SECRET_KEY", "your-secret-key-change-in-production")}\n\n'
        )

        f.write("# ─── CORS Origins ──────────────────────────\n")
        f.write(
            f'FRONTEND_ORIGINS={env_data.get("FRONTEND_ORIGINS", "http://localhost:5000,http://localhost:3000")}\n\n'
        )

        f.write("# ─── Rate Limiting ─────────────────────────\n")
        f.write(
            f'RATELIMIT_STORAGE_URL={env_data.get("RATELIMIT_STORAGE_URL", "memory://")}\n'
        )


def configure_supabase():
    """Interactive Supabase configuration"""
    print("\n" + "=" * 60)
    print("FLAVOUR FLEET — Supabase Configuration Helper")
    print("=" * 60 + "\n")

    env_path = get_env_file()
    existing_data = read_env_file(env_path)

    print("📋 Step 1: Get Your Supabase Credentials")
    print("  1. Go to https://supabase.com")
    print("  2. Create new project (or open existing)")
    print("  3. Go to Settings → API")
    print("  4. Copy 'URL' and 'Service Role Key'")
    print()

    print("🔑 Step 2: Enter Your Credentials")
    print()

    supabase_url = input(
        "Enter SUPABASE_URL (https://YOUR_PROJECT_ID.supabase.co): "
    ).strip()
    if not supabase_url:
        supabase_url = existing_data.get(
            "SUPABASE_URL", "https://YOUR_PROJECT_ID.supabase.co"
        )

    print()
    supabase_key = input("Enter SUPABASE_SERVICE_KEY: ").strip()
    if not supabase_key:
        supabase_key = existing_data.get("SUPABASE_SERVICE_KEY", "YOUR_SERVICE_KEY")

    print()
    print("ℹ️  For frontend, you'll need ANON_KEY (not Service Key)")
    print("    You can set it in index.html & login.html")

    # Update data
    new_data = existing_data.copy()
    new_data["SUPABASE_URL"] = supabase_url
    new_data["SUPABASE_SERVICE_KEY"] = supabase_key

    # Write to file
    write_env_file(env_path, new_data)

    print("\n✅ Configuration saved to backend/.env")
    print("\n📝 Next Steps:")
    print("  1. Set up PostgreSQL tables (see SUPABASE_INTEGRATION.md)")
    print("  2. Add ANON_KEY to frontend in index.html & login.html")
    print("  3. Restart Flask server: python backend/app.py")
    print("  4. Test at http://localhost:5000/login.html")
    print("\n" + "=" * 60 + "\n")


def validate_supabase():
    """Validate Supabase configuration"""
    print("\n" + "=" * 60)
    print("FLAVOUR FLEET — Supabase Configuration Validator")
    print("=" * 60 + "\n")

    env_path = get_env_file()
    env_data = read_env_file(env_path)

    print("Checking Supabase configuration...\n")

    checks = []

    # Check .env file
    if env_path.exists():
        checks.append(("✅", ".env file exists"))
    else:
        checks.append(("❌", ".env file not found"))

    # Check SUPABASE_URL
    url = env_data.get("SUPABASE_URL")
    if url and url.startswith("https://") and ".supabase.co" in url:
        checks.append(("✅", "SUPABASE_URL is valid format"))
    else:
        checks.append(("⚠️ ", "SUPABASE_URL not configured or invalid"))

    # Check SUPABASE_SERVICE_KEY
    key = env_data.get("SUPABASE_SERVICE_KEY")
    if key and key.startswith("eyJ"):
        checks.append(("✅", "SUPABASE_SERVICE_KEY looks valid"))
    else:
        checks.append(("⚠️ ", "SUPABASE_SERVICE_KEY not set or invalid"))

    # Try import
    try:
        from supabase import create_client

        checks.append(("✅", "supabase package installed"))
    except ImportError:
        checks.append(("❌", "supabase package not installed"))

    # Display results
    for status, message in checks:
        print(f"  {status} {message}")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        validate_supabase()
    else:
        configure_supabase()

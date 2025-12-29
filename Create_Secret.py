import argparse
import requests
import sys


def parse_key_values(pairs):
    data = {}
    for item in pairs:
        if "=" not in item:
            raise SystemExit(f"Invalid key format: {item}")
        k, v = item.split("=", 1)
        data[k] = v
    return data


def main():
    parser = argparse.ArgumentParser(
        description="Create Kubernetes Secret via Kubernetes API (kubectl proxy)"
    )

    parser.add_argument("--api-url", required=True, help="Kubernetes API URL (via kubectl proxy)")
    parser.add_argument("--namespace", required=True, help="Kubernetes namespace")
    parser.add_argument("--name", required=True, help="Secret name")
    parser.add_argument("--key", action="append", required=True, help="key=value")

    args = parser.parse_args()

    secret_data = parse_key_values(args.key)

    secret_payload = {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": args.name,
            "namespace": args.namespace,
        },
        "type": "Opaque",
        "stringData": secret_data,
    }

    url = f"{args.api_url}/api/v1/namespaces/{args.namespace}/secrets"

    headers = {
        "Content-Type": "application/json",
    }

    resp = requests.post(url, json=secret_payload, headers=headers)

    if resp.status_code >= 300:
        print(f"ERROR {resp.status_code}: {resp.text}")
        sys.exit(1)

    print(f"Secret '{args.name}' created successfully in namespace '{args.namespace}'")


if __name__ == "__main__":
    main()

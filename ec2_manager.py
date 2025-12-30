import argparse
import boto3
import sys


def list_instances(ec2):
    response = ec2.describe_instances()

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            state = instance["State"]["Name"]
            instance_type = instance["InstanceType"]

            print(f"{instance_id} | {state} | {instance_type}")


def start_instance(ec2, instance_id):
    ec2.start_instances(InstanceIds=[instance_id])
    print(f"Start initiated for instance {instance_id}")


def stop_instance(ec2, instance_id):
    ec2.stop_instances(InstanceIds=[instance_id])
    print(f"Stop initiated for instance {instance_id}")


def print_state(ec2, instance_id):
    response = ec2.describe_instances(InstanceIds=[instance_id])

    instance = response["Reservations"][0]["Instances"][0]
    state = instance["State"]["Name"]

    print(f"Instance {instance_id} state: {state}")


def main():
    parser = argparse.ArgumentParser(description="EC2 management using boto3")

    parser.add_argument(
        "action",
        choices=["list", "start", "stop", "state"],
        help="Action to perform",
    )

    parser.add_argument(
        "--instance-id",
        help="EC2 instance ID (required for start/stop/state)",
    )

    args = parser.parse_args()

    ec2 = boto3.client("ec2")

    if args.action == "list":
        list_instances(ec2)

    elif args.action in {"start", "stop", "state"}:
        if not args.instance_id:
            print("--instance-id is required for this action")
            sys.exit(1)

        if args.action == "start":
            start_instance(ec2, args.instance_id)

        elif args.action == "stop":
            stop_instance(ec2, args.instance_id)

        elif args.action == "state":
            print_state(ec2, args.instance_id)


if __name__ == "__main__":
    main()

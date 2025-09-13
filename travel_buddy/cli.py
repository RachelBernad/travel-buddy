import argparse

from travel_buddy.graphs.basic_graph import run_graph


def main():
    parser = argparse.ArgumentParser(description="Travel Buddy LLM CLI")
    parser.add_argument("prompt", nargs="+", help="User prompt")
    args = parser.parse_args()

    prompt = " ".join(args.prompt)


    state = run_graph(prompt)
    print(state.get("answer", ""))


if __name__ == "__main__":
    main()

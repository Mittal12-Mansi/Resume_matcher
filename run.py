import sys
import os
import argparse
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="AI Resume ↔ Job Description Matcher Runner")
    parser.add_argument("--mode", choices=["api", "streamlit", "eval", "generate"], default="api",
                        help="Mode to run: 'api' (FastAPI web server & UI dashboard), 'streamlit', 'eval' (benchmark evaluation), or 'generate' (dataset generation)")
    parser.add_argument("--port", type=int, default=8000, help="Port for FastAPI server (default: 8000)")

    args = parser.parse_args()

    if args.mode == "generate":
        print("[Run] Generating datasets...")
        from data_generator import main as gen_main
        gen_main()

    elif args.mode == "eval":
        print("[Run] Running model evaluation benchmark...")
        from eval_engine import main as eval_main
        eval_main()

    elif args.mode == "streamlit":
        print("[Run] Launching Streamlit App...")
        os.system("streamlit run app.py")

    else:
        print(f"[Run] Starting FastAPI Production Server on http://localhost:{args.port}...")
        uvicorn.run("api_app:app", host="0.0.0.0", port=args.port, reload=True)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Run the benchmark: models × tasks × conditions × repetitions.

    python3 bench/run.py --models haiku --reps 3 --workers 4 \
        --venv /path/to/venv-with-pytest --workdir /tmp/seam-runs --out bench/results/pilot-haiku

Agent repos live under --workdir (keep it outside this repository so agents
can't stumble on SKILL.md); transcripts, diffs and grades are saved under --out.
Re-running the same command skips runs that already have a result.json.
"""
import argparse
import json
import shutil
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from harness import CONDITIONS, TASKS, agent_env, grade, prepare_repo, run_agent, task_prompt, transcript_metrics


def one_run(model, task, condition, rep, args) -> dict:
    run_id = f"{model}/{task}/{condition}/r{rep}"
    out = args.out / model / task / condition / f"r{rep}"
    if (out / "result.json").exists():
        return json.loads((out / "result.json").read_text())
    work = args.workdir / model / task / condition / f"r{rep}"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    out.mkdir(parents=True, exist_ok=True)
    home = work / "home"
    home.mkdir()
    env = agent_env(home, args.venv / "bin")

    repo = prepare_repo(work, condition)
    prompt = task_prompt(task, condition)
    (out / "prompt.txt").write_text(prompt)
    started = time.time()
    rc = run_agent(repo, prompt, model, out / "transcript.jsonl", env,
                   effort=args.effort, budget_usd=args.budget, timeout_s=args.timeout)
    result = {
        "run_id": run_id, "model": model, "task": task, "condition": condition, "rep": rep,
        "effort": args.effort, "exit_code": rc, "wall_s": round(time.time() - started, 1),
    }
    result.update(transcript_metrics(out / "transcript.jsonl", repo))
    result.update(grade(repo, task, out, env))
    (out / "result.json").write_text(json.dumps(result, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", default="haiku")
    parser.add_argument("--tasks", default=",".join(TASKS))
    parser.add_argument("--conditions", default=",".join(CONDITIONS))
    parser.add_argument("--reps", type=int, default=3)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--effort", default=None)
    parser.add_argument("--budget", type=float, default=5.0, help="max USD per agent run")
    parser.add_argument("--timeout", type=int, default=1800, help="seconds per agent run")
    parser.add_argument("--venv", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out = args.out.resolve()

    jobs = [
        (model, task, condition, rep)
        for rep in range(1, args.reps + 1)
        for model in args.models.split(",")
        for task in args.tasks.split(",")
        for condition in args.conditions.split(",")
    ]
    print(f"{len(jobs)} runs, {args.workers} in parallel", flush=True)
    with ThreadPoolExecutor(args.workers) as pool:
        futures = {pool.submit(one_run, *job, args): job for job in jobs}
        for done, future in enumerate(as_completed(futures), 1):
            job = futures[future]
            try:
                r = future.result()
                print(f"[{done}/{len(jobs)}] {r['run_id']}: hidden {r['hidden_passed']}/{r['hidden_total']}"
                      f" visible_green={r['visible_green']} cost=${r.get('cost_usd') or 0:.2f}"
                      f" skills={r['skills_invoked']}", flush=True)
            except Exception:  # noqa: BLE001
                print(f"[{done}/{len(jobs)}] {'/'.join(map(str, job))}: HARNESS ERROR\n{traceback.format_exc()}",
                      flush=True)


if __name__ == "__main__":
    main()

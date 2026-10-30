#!/usr/bin/env bash
set -euo pipefail

REMOTE=${REMOTE:-origin}
MAIN_BRANCH=${MAIN_BRANCH:-main}
BASE_REF=${BASE_REF:-$REMOTE/$MAIN_BRANCH}

dry_run=0
force=0

usage() {
  cat <<'EOF'
Usage: make branch-update [ARGS="--dry-run --force"]

Delete the current development branch's remote branch, rebase it onto the
latest origin/main, and fast-forward the local main branch.

This command only supports development branches. It refuses to run on the
main/default branch.

Options:
  --dry-run   Print the actions without changing anything.
  --force     Delete the remote branch even when it contains changes that are
              not present in the local branch or origin/main.
  -h, --help  Show this help.

Environment:
  REMOTE       remote name (default: origin)
  MAIN_BRANCH  local main branch (default: main)
  BASE_REF     base ref (default: $REMOTE/$MAIN_BRANCH)
EOF
}

die() {
  echo "error: $*" >&2
  exit 1
}

run() {
  if [ "$dry_run" -eq 1 ]; then
    printf '[dry-run] %s\n' "$*"
  else
    "$@"
  fi
}

has_ref() {
  git show-ref --verify --quiet "$1"
}

for arg in "$@"; do
  case "$arg" in
    --dry-run) dry_run=1 ;;
    --force) force=1 ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; die "unknown argument: $arg" ;;
  esac
done

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "not inside a git repository"
branch=$(git symbolic-ref --quiet --short HEAD) || die "HEAD is detached; check out a branch first"

default_branch=$(git symbolic-ref --quiet --short "refs/remotes/$REMOTE/HEAD" 2>/dev/null || true)
default_branch=${default_branch#"$REMOTE/"}
if [ "$branch" = "$MAIN_BRANCH" ] || { [ -n "$default_branch" ] && [ "$branch" = "$default_branch" ]; }; then
  die "branch-update only supports development branches; refusing to run on $branch"
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
  die "working tree has uncommitted changes; commit or stash them first"
fi

echo "==> Fetching $REMOTE"
git fetch --prune "$REMOTE"
has_ref "refs/remotes/$BASE_REF" || die "missing $BASE_REF after fetch"

if has_ref "refs/heads/$MAIN_BRANCH"; then
  echo "==> Fast-forwarding local $MAIN_BRANCH to $BASE_REF"
  if [ "$dry_run" -eq 1 ]; then
    echo "[dry-run] git switch $MAIN_BRANCH && git merge --ff-only $BASE_REF && git switch $branch"
  else
    git switch --quiet "$MAIN_BRANCH"
    if ! git merge --ff-only --quiet "$BASE_REF"; then
      git switch --quiet "$branch"
      die "local $MAIN_BRANCH has diverged from $BASE_REF; resolve it manually"
    fi
    git switch --quiet "$branch"
  fi
fi

remote_ref="refs/remotes/$REMOTE/$branch"
if has_ref "$remote_ref"; then
  if [ "$force" -eq 0 ]; then
    safe=0
    if git merge-base --is-ancestor "$remote_ref" HEAD; then safe=1; fi
    if git merge-base --is-ancestor "$remote_ref" "$BASE_REF"; then safe=1; fi
    if git diff --quiet "$remote_ref" HEAD; then safe=1; fi
    if git diff --quiet "$remote_ref" "$BASE_REF"; then safe=1; fi
    if [ "$safe" -ne 1 ]; then
      cat >&2 <<EOF
error: refusing to delete $REMOTE/$branch because it contains changes that are
       not present in the local branch or in $BASE_REF.
       Re-run with --force if you really want to drop those changes.
EOF
      exit 1
    fi
  fi

  echo "==> Deleting remote branch $REMOTE/$branch"
  run git push "$REMOTE" --delete "$branch"
  if [ "$dry_run" -eq 0 ]; then
    git update-ref -d "$remote_ref" 2>/dev/null || true
  fi
else
  echo "==> Remote branch $REMOTE/$branch does not exist; skipping deletion"
fi

upstream_remote=$(git config --get "branch.$branch.remote" || true)
upstream_merge=$(git config --get "branch.$branch.merge" || true)
if [ "$upstream_remote" = "$REMOTE" ] && [ "$upstream_merge" = "refs/heads/$branch" ]; then
  echo "==> Removing upstream tracking for $branch"
  run git branch --unset-upstream "$branch"
fi

echo "==> Rebasing $branch onto $BASE_REF"
if [ "$dry_run" -eq 1 ]; then
  echo "[dry-run] git rebase $BASE_REF"
else
  if ! git rebase "$BASE_REF"; then
    git rebase --abort >/dev/null 2>&1 || true
    die "rebase failed; aborted and left $branch unchanged"
  fi
fi

ahead=$(git rev-list --count "$BASE_REF..HEAD")
behind=$(git rev-list --count "HEAD..$BASE_REF")

echo
echo "==> Done"
echo "  branch: $branch @ $(git rev-parse --short HEAD)"
echo "  base:   $BASE_REF @ $(git rev-parse --short "$BASE_REF")"
echo "  ahead:  $ahead"
echo "  behind: $behind"
if [ "$dry_run" -eq 1 ]; then
  echo "  (dry-run: no branch changes)"
else
  echo "  next:   git push -u $REMOTE $branch"
fi

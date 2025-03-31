import subprocess
import os
import shutil

def get_branches():
    result = subprocess.run(
        ["git", "branch", "--list", "--remote"],
        capture_output=True, text=True, check=True
    )
    branches = [
        line.strip().replace("origin/", "")
        for line in result.stdout.strip().split("\n")
        if "HEAD" not in line
    ]
    print("Available branches:", branches)
    return branches

def deploy_to_github_pages(branch_name):
    print(f"Deploying branch: {branch_name}")

    # gh-pages に切り替え
    subprocess.run(["git", "switch", "gh-pages"], check=True)

    # 最新の状態を取得
    subprocess.run(["git", "pull", "origin", "gh-pages"], check=True)

    # サブディレクトリを作成
    version_folder = f"version-{branch_name}"
    os.makedirs(version_folder, exist_ok=True)

    # 一時作業ディレクトリを作成
    temp_dir = f"temp-{branch_name}"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)

    # 対象ブランチをチェックアウト（worktreeを利用）
    subprocess.run(["git", "worktree", "add", temp_dir, branch_name], check=True)

    # 一時ディレクトリから `version_folder` にコピー
    for item in os.listdir(temp_dir):
        if item not in [".git", ".github"]:
            src_path = os.path.join(temp_dir, item)
            dest_path = os.path.join(version_folder, item)
            if os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
            else:
                shutil.copy2(src_path, dest_path)

    # worktree を削除
    subprocess.run(["git", "worktree", "remove", temp_dir], check=True)
    shutil.rmtree(temp_dir, ignore_errors=True)

    # 変更をコミット
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Add {branch_name} to gh-pages"], check=True)

    # gh-pagesにプッシュ
    subprocess.run(["git", "push", "origin", "gh-pages"], check=True)

if __name__ == "__main__":
    branches = get_branches()
    branches_to_deploy = [branch for branch in branches if branch not in ["main", "gh-pages"]]

    print("Branches to deploy:", branches_to_deploy)

    for branch in branches_to_deploy:
        deploy_to_github_pages(branch)

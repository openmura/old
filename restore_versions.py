import os
import subprocess
from datetime import datetime

# コミット履歴を取得し、2024年12月27日以降のものだけ返す
def get_commits():
    result = subprocess.run(
        ["git", "log", "--pretty=format:%H %ad", "--date=short"],
        capture_output=True, text=True
    )
    # 取得したコミットを日付でフィルタリング
    commits = [line.split(" ") for line in result.stdout.strip().split("\n")]
    # 2024年12月27日以降のコミットだけ返す
    filtered_commits = [
        (commit_id, commit_date) for commit_id, commit_date in commits
        if datetime.strptime(commit_date, "%Y-%m-%d") > datetime.strptime("2024-12-27", "%Y-%m-%d")
    ]
    return filtered_commits

# 各コミットをブランチ化して整理
def process_commits(commits):
    # コミットをローカルでまとめるためのステージング
    staged_changes = []

    for commit_id, commit_date in commits:
        branch_name = f"version-{commit_date}"
        folder_path = f"versions/{branch_name}"

        print(f"⏳ Processing {branch_name} ({commit_id})...")

        # コミットが存在するかチェック
        result = subprocess.run(["git", "show", commit_id], capture_output=True)
        if result.returncode != 0:
            print(f"❌ Skipping {commit_id}: Commit not found")
            continue

        # ブランチ作成
        subprocess.run(["git", "checkout", "-b", branch_name, commit_id])

        # フォルダ作成＆ファイル移動（Windows向け）
        os.makedirs(folder_path, exist_ok=True)
        subprocess.run(["powershell", "-Command", f"Get-ChildItem -Path . -File -Exclude '.git', '.github', 'versions' | Move-Item -Destination {folder_path}"])

        # ローカルで変更をステージ
        staged_changes.append(f"Move {commit_date} version into {folder_path}")

        # main/master に戻る
        subprocess.run(["git", "checkout", "main"])

    # 一度にまとめてコミット＆プッシュ
    if staged_changes:
        # ステージした変更をまとめてコミット
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "Move versions to their respective folders"])

        # プッシュ
        subprocess.run(["git", "push", "origin", "main"])

        print("✅ Changes pushed successfully!")

if __name__ == "__main__":
    commits = get_commits()
    process_commits(commits)

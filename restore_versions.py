import os
import subprocess
from datetime import datetime

# コミット履歴を取得
def get_commits():
    result = subprocess.run(
        ["git", "log", "--pretty=format:%H %ad", "--date=short"],
        capture_output=True, text=True
    )
    return [line.split(" ") for line in result.stdout.strip().split("\n")]

# 2024年12月27日以降のコミットはプッシュしない
def is_after_cutoff(commit_date, cutoff_date="2024-12-27"):
    return datetime.strptime(commit_date, "%Y-%m-%d") > datetime.strptime(cutoff_date, "%Y-%m-%d")

# 各コミットをブランチ化して整理
def process_commits(commits):
    for commit_id, commit_date in commits:
        # 2024年12月27日以降のコミットはプッシュしない
        if is_after_cutoff(commit_date):
            print(f"❌ Skipping commit {commit_id} from {commit_date}: After cutoff date.")
            continue

        branch_name = f"version-{commit_date}"
        folder_path = f"versions/{branch_name}"

        print(f"⏳ Processing {branch_name} ({commit_id})...")

        # コミットが存在するかチェック
        result = subprocess.run(["git", "show", commit_id], capture_output=True)
        if result.returncode != 0:
            print(f"❌ Skipping {commit_id}: Commit not found")
            continue

        # 既存のブランチがあれば削除して新たに作成
        result = subprocess.run(["git", "branch", "--list", branch_name], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"⚠️ Branch {branch_name} already exists. Deleting and recreating it.")
            subprocess.run(["git", "branch", "-D", branch_name])  # 強制的に削除
        subprocess.run(["git", "checkout", "-b", branch_name, commit_id])  # 新しくブランチ作成

        # フォルダ作成＆ファイル移動（Windows向け）
        os.makedirs(folder_path, exist_ok=True)
        subprocess.run(["powershell", "-Command", f"Get-ChildItem -Path . -File -Exclude '.git', '.github', 'versions' | Move-Item -Destination {folder_path}"])

        # コミットをローカルで行う（この時点でまだpushしない）
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", f"Move {commit_date} version into {folder_path}"])

        print(f"✅ {branch_name} committed successfully!")

        # main/master に戻る
        subprocess.run(["git", "checkout", "main"])

    # 最後に一度だけ main ブランチにプッシュする
    subprocess.run(["git", "push", "origin", "main"])

if __name__ == "__main__":
    commits = get_commits()
    process_commits(commits)

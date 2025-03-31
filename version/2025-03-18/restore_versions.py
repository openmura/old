import os
import subprocess

# コミット履歴を取得
def get_commits():
    result = subprocess.run(
        ["git", "log", "--pretty=format:%H %ad", "--date=short"],
        capture_output=True, text=True
    )
    return [line.split(" ") for line in result.stdout.strip().split("\n")]

# 各コミットをブランチ化して整理
def process_commits(commits):
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

        # コミット＆プッシュ
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", f"Move {commit_date} version into {folder_path}"])
        subprocess.run(["git", "push", "origin", branch_name])

        print(f"✅ {branch_name} pushed successfully!")

        # main/master に戻る
        subprocess.run(["git", "checkout", "main"])
    
if __name__ == "__main__":
    commits = get_commits()
    process_commits(commits)

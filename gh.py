import subprocess
import os
import shutil

# GitHubのブランチ名を取得
def get_branches():
    result = subprocess.run(
        ["git", "branch", "--list", "--remote"],
        capture_output=True, text=True
    )
    # "HEAD -> main" を除外し、実際のブランチ名だけを取得
    branches = [
        line.strip().replace("origin/", "") 
        for line in result.stdout.strip().split("\n") 
        if "HEAD" not in line  # "HEAD -> main" を除外
    ]
    print("Available branches:", branches)  # ブランチ名を出力してデバッグ
    return branches

def deploy_to_github_pages(branch_name):
    print(f"Deploying branch: {branch_name}")  # デバッグ用
    # gh-pagesブランチに切り替え
    subprocess.run(["git", "checkout", "gh-pages"], check=True)

    # 対象のブランチからファイルを取得
    subprocess.run(["git", "checkout", branch_name, "--", "."], check=True)

    # サブディレクトリを作成してファイルを移動
    version_folder = f"version-{branch_name}"
    os.makedirs(version_folder, exist_ok=True)

    # 現在のディレクトリのファイルをサブディレクトリに移動
    for item in os.listdir('.'):
        if item != version_folder and item != ".git" and item != ".github":
            item_path = os.path.join(os.getcwd(), item)  # 現在のファイルの絶対パスを取得
            dest_path = os.path.join(os.getcwd(), version_folder, item)  # 移動先の絶対パスを取得
            if os.path.isdir(item_path):
                shutil.move(item_path, dest_path)  # ディレクトリを移動
            else:
                shutil.move(item_path, dest_path)  # ファイルを移動

    # 変更をコミット
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Add {branch_name} to gh-pages"], check=True)

    # gh-pagesにプッシュ
    subprocess.run(["git", "push", "origin", "gh-pages"], check=True)

if __name__ == "__main__":
    # ブランチリストを取得
    branches = get_branches()

    # main と gh-pages を除外して他のブランチで処理
    branches_to_deploy = [branch for branch in branches if branch != "main" and branch != "gh-pages"]
    
    print("Branches to deploy:", branches_to_deploy)  # デバッグ用

    # すべてのブランチに対してデプロイを実行
    for branch in branches_to_deploy:
        # すでに gh-pages にそのブランチがあるか確認
        try:
            result = subprocess.run(
                ["git", "branch", "--list", branch],
                capture_output=True, text=True
            )
            if branch in result.stdout:
                print(f"Branch {branch} already exists in gh-pages, skipping deployment.")
                continue  # すでに存在する場合はスキップ
        except subprocess.CalledProcessError:
            pass  # エラーが発生した場合は無視

        deploy_to_github_pages(branch)

# BoxTester

Box上ファイル操作用のシンプルなCLIツールです。`box_transfer.py`を利用して、
ローカル→Boxへのアップロード、Box→ローカルへのダウンロードの両方を行えます。

## 事前準備
1. Python 3.10+ と `pip` を用意します。
2. 依存ライブラリをインストールします。

   ```bash
   pip install -r requirements.txt
   ```

3. BoxのDeveloper Tokenを取得します（次節参照）。

## Box Developer Tokenの取得方法
1. [Box Developer Console](https://app.box.com/developers/console)にアクセスします。
2. "Custom App" → "User Authentication (OAuth 2.0)" を選択し、任意のアプリ名で作成します。
3. アプリの設定画面で "Developer Token" セクションにある「Generate Token」を押します。
4. 表示された文字列を控えてください（有効期限は12時間です。期限が切れたら再度生成します）。
5. フォルダ／ファイルIDは、ブラウザで対象を開いた時のURL末尾（`.../folder/<ID>` や `.../file/<ID>`）から取得できます。

## Developer Tokenの安全な渡し方
`box_transfer.py`はDeveloper Tokenを以下の順に探索します。

1. コマンドライン引数 `--token` の値
2. 環境変数 `BOX_DEVELOPER_TOKEN`

常に引数で渡しても構いませんが、毎回入力するのが面倒な場合は環境変数を設定すると便利です。OS別の例は以下の通りです（トークンは12時間ごとに更新してください）。

### macOS / Linux (bash, zshなど)
```bash
export BOX_DEVELOPER_TOKEN="ここに発行したトークン"
```
上記を `~/.bashrc` や `~/.zshrc` に追記すると、次回以降のシェルでも自動で読み込まれます。

### Windows PowerShell
```powershell
[Environment]::SetEnvironmentVariable("BOX_DEVELOPER_TOKEN", "発行したトークン", "User")
```
PowerShellを開き直すと利用できます。期限が切れたら同じ手順で更新してください。

### .envファイルに保存して読み込む
シェル上にトークンを残したくない場合は、以下のようなファイルを作成し、必要なときだけ `source`（PowerShellでは `Get-Content` 等）で読み込む方法もあります。

```bash
echo 'export BOX_DEVELOPER_TOKEN="発行したトークン"' > ~/.box_token.env
source ~/.box_token.env
```

## 使い方
`box_transfer.py`はサブコマンド型のCLIです。Developer Tokenは前述の方法で準備してから実行してください。

### アップロード
ローカルのファイル／フォルダをBox上の指定フォルダにアップロードします。
```bash
python box_transfer.py upload <LOCAL_PATH> <BOX_FOLDER_ID>
```
- フォルダを指定した場合は再帰的にサブフォルダ・ファイルをアップロードします。
- すでに同名ファイルが存在する場合は新しいバージョンとして上書きします。

### ダウンロード
Box上のファイルまたはフォルダをローカルにダウンロードします。
```bash
python box_transfer.py download <ITEM_ID> <file|folder> <DEST_DIR>
```
- `<file|folder>`でIDが指すリソースのタイプを指定します。
- `<DEST_DIR>`が存在しない場合は自動で作成されます。
- フォルダを指定した場合は中身を再帰的に取得します。

## 実行例
### 1. Developer Tokenを環境変数に設定する
```bash
export BOX_DEVELOPER_TOKEN="xxxxxxxx"
```

### 2. ローカルの`./reports`フォルダをBoxのフォルダID `123456789` へアップロード
```bash
python box_transfer.py upload ./reports 123456789
```

### 3. BoxファイルID `987654321` を `~/Downloads/box_files` にダウンロード
```bash
python box_transfer.py download 987654321 file ~/Downloads/box_files
```
PowerShellの場合も同じコマンド体系で動作します（パス記法のみ適宜変更してください）。

## トラブルシュート
- Developer Tokenの有効期限（通常12時間）が切れていないか確認してください。
- `boxsdk.exception.BoxAPIException` が発生した場合は、フォルダID／ファイルID、
  権限、ネットワーク状況を確認してください。
- `BOX_DEVELOPER_TOKEN` を環境変数に設定しているのに認識されない場合は、
  そのシェルで `echo $BOX_DEVELOPER_TOKEN`（PowerShellでは `$env:BOX_DEVELOPER_TOKEN`）を実行し、
  値がセットされているか確認してください。

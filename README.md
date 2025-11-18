# BoxTester

Box上ファイル操作用のシンプルなCLIツールです。`box_transfer.py`を利用して、
ローカル→Boxへのアップロード、Box→ローカルへのダウンロードの両方を行えます。

## 事前準備
1. [Box Developer Console](https://app.box.com/developers/console)でDeveloper Tokenを取得します。
2. Python 3.10+ と `pip` を用意します。
3. 依存ライブラリをインストールします。

```bash
pip install -r requirements.txt
```

## 使い方
`box_transfer.py`はサブコマンド型のCLIです。Developer Tokenは引数`--token`で渡すか、
環境変数`BOX_DEVELOPER_TOKEN`を設定してください。

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

## トラブルシュート
- Developer Tokenの有効期限（通常12時間）が切れていないか確認してください。
- `boxsdk.exception.BoxAPIException` が発生した場合は、フォルダID／ファイルID、
  権限、ネットワーク状況を確認してください。

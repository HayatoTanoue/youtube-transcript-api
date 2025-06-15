FROM python:3.9-slim

WORKDIR /app

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Poetry のインストール
RUN curl -sSL https://install.python-poetry.org | python3 -

# PATH に poetry を追加
ENV PATH="/root/.local/bin:$PATH"

# 依存関係のコピーとインストール
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && \
    poetry install --with test,dev --no-root

# pytest-covを追加インストール（pyproject.tomlに含まれていない場合）
RUN pip install pytest-cov

# アプリケーションコードのコピー
COPY . .

# プロジェクト自体のインストール
RUN poetry install --only-root

# Git設定（コンテナ内でgitコマンドを使用する場合）
RUN git config --global --add safe.directory /app

CMD ["/bin/bash"]
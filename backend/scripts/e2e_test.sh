#!/usr/bin/env bash
###############################################################################
# E2Eフロー検証スクリプト
#
# 機能: サインアップ → ログイン → ユーザー情報取得の自動テスト
# 使用方法:
#   ./backend/scripts/e2e_test.sh
#   または
#   bash backend/scripts/e2e_test.sh
#
# 前提条件:
#   - Docker Composeサービスが起動していること
#   - バックエンドAPI (http://localhost:8000) が稼働していること
#
# 作成日: 2025-11-10
# 作成者: Worker3
###############################################################################

set -euo pipefail

###############################################################################
# 設定
###############################################################################

# API Base URL
BASE_URL="${API_BASE_URL:-http://localhost:8000}"

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# テストユーザーデータ（ユニーク性確保のためタイムスタンプ使用）
TIMESTAMP=$(date +%s)
USERNAME="e2e_test_${TIMESTAMP}"
EMAIL="e2e_test_${TIMESTAMP}@example.com"
PASSWORD="E2ETestPass123!"
KATEGORI="学生"
GAKUSEKI_BANGO="E2E${TIMESTAMP:(-6)}"
FACULTY="工学部"

# 一時ファイル
RESPONSE_FILE=$(mktemp)
trap "rm -f ${RESPONSE_FILE}" EXIT

# テスト結果カウンター
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

###############################################################################
# ヘルパー関数
###############################################################################

print_header() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

print_step() {
    echo -e "${YELLOW}► $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASSED_TESTS++))
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
    ((FAILED_TESTS++))
}

print_info() {
    echo -e "  $1"
}

check_jq() {
    if command -v jq &> /dev/null; then
        return 0
    else
        return 1
    fi
}

extract_json_value() {
    local json="$1"
    local key="$2"

    if check_jq; then
        echo "$json" | jq -r "$key"
    else
        # jqがない場合、シンプルなgrep/sedで抽出
        echo "$json" | grep -o "\"${key}\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" | sed 's/.*:"\(.*\)"/\1/'
    fi
}

###############################################################################
# テスト関数
###############################################################################

test_health_check() {
    print_step "ヘルスチェック: GET ${BASE_URL}/health"
    ((TOTAL_TESTS++))

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" "${BASE_URL}/health")
    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "ヘルスチェック成功 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 0
    else
        print_error "ヘルスチェック失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_signup() {
    print_step "サインアップ: POST ${BASE_URL}/auth/signup"
    ((TOTAL_TESTS++))

    # JSONリクエストボディ
    REQUEST_BODY=$(cat <<EOF
{
  "username": "${USERNAME}",
  "email": "${EMAIL}",
  "password": "${PASSWORD}",
  "kategori": "${KATEGORI}",
  "gakuseki_bango": "${GAKUSEKI_BANGO}",
  "faculty": "${FACULTY}"
}
EOF
)

    print_info "リクエストボディ:"
    echo "$REQUEST_BODY" | sed 's/^/    /'

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X POST "${BASE_URL}/auth/signup" \
        -H "Content-Type: application/json" \
        -d "$REQUEST_BODY")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 201 ]; then
        print_success "サインアップ成功 (HTTP $HTTP_CODE)"

        # ユーザーIDを抽出
        if check_jq; then
            USER_ID=$(echo "$RESPONSE" | jq -r '.id')
            CREATED_USERNAME=$(echo "$RESPONSE" | jq -r '.username')
            CREATED_EMAIL=$(echo "$RESPONSE" | jq -r '.email')
            print_info "作成されたユーザーID: $USER_ID"
            print_info "ユーザー名: $CREATED_USERNAME"
            print_info "Email: $CREATED_EMAIL"
        else
            print_info "レスポンス: $RESPONSE"
        fi
        return 0
    else
        print_error "サインアップ失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_login() {
    print_step "ログイン: POST ${BASE_URL}/auth/token"
    ((TOTAL_TESTS++))

    # OAuth2 form data（application/x-www-form-urlencoded）
    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X POST "${BASE_URL}/auth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=${USERNAME}&password=${PASSWORD}")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "ログイン成功 (HTTP $HTTP_CODE)"

        # アクセストークンを抽出
        if check_jq; then
            ACCESS_TOKEN=$(echo "$RESPONSE" | jq -r '.access_token')
            TOKEN_TYPE=$(echo "$RESPONSE" | jq -r '.token_type')
            print_info "トークンタイプ: $TOKEN_TYPE"
            print_info "アクセストークン: ${ACCESS_TOKEN:0:20}..."
        else
            # jqがない場合、grep/sedで抽出
            ACCESS_TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"\(.*\)"/\1/')
            print_info "アクセストークン取得成功"
        fi

        # グローバル変数に保存
        export ACCESS_TOKEN
        return 0
    else
        print_error "ログイン失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_get_user_info() {
    print_step "ユーザー情報取得: GET ${BASE_URL}/users/me"
    ((TOTAL_TESTS++))

    if [ -z "${ACCESS_TOKEN:-}" ]; then
        print_error "アクセストークンが設定されていません"
        return 1
    fi

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X GET "${BASE_URL}/users/me" \
        -H "Authorization: Bearer ${ACCESS_TOKEN}")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "ユーザー情報取得成功 (HTTP $HTTP_CODE)"

        if check_jq; then
            FETCHED_USERNAME=$(echo "$RESPONSE" | jq -r '.username')
            FETCHED_EMAIL=$(echo "$RESPONSE" | jq -r '.email')
            FETCHED_KATEGORI=$(echo "$RESPONSE" | jq -r '.kategori')
            FETCHED_GAKUSEKI=$(echo "$RESPONSE" | jq -r '.gakuseki_bango')

            print_info "取得情報:"
            print_info "  - ユーザー名: $FETCHED_USERNAME"
            print_info "  - Email: $FETCHED_EMAIL"
            print_info "  - カテゴリ: $FETCHED_KATEGORI"
            print_info "  - 学籍番号: $FETCHED_GAKUSEKI"

            # データ整合性チェック
            if [ "$FETCHED_USERNAME" = "$USERNAME" ] && [ "$FETCHED_EMAIL" = "$EMAIL" ]; then
                print_success "データ整合性確認: ユーザー情報が一致"
            else
                print_error "データ整合性エラー: ユーザー情報が不一致"
                return 1
            fi
        else
            print_info "レスポンス: $RESPONSE"
        fi
        return 0
    else
        print_error "ユーザー情報取得失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

###############################################################################
# メイン実行
###############################################################################

main() {
    print_header "E2Eフロー検証テスト開始"

    echo "テスト設定:"
    echo "  - API Base URL: $BASE_URL"
    echo "  - テストユーザー名: $USERNAME"
    echo "  - テストEmail: $EMAIL"
    echo "  - jq利用可能: $(check_jq && echo 'Yes' || echo 'No')"
    echo ""

    # Step 0: ヘルスチェック
    if ! test_health_check; then
        echo ""
        echo -e "${RED}ヘルスチェック失敗。APIサーバーが起動していない可能性があります。${NC}"
        exit 1
    fi

    # Step 1: サインアップ
    echo ""
    if ! test_signup; then
        echo ""
        echo -e "${RED}サインアップ失敗。テスト中断。${NC}"
        exit 1
    fi

    # Step 2: ログイン
    echo ""
    if ! test_login; then
        echo ""
        echo -e "${RED}ログイン失敗。テスト中断。${NC}"
        exit 1
    fi

    # Step 3: ユーザー情報取得
    echo ""
    if ! test_get_user_info; then
        echo ""
        echo -e "${RED}ユーザー情報取得失敗。${NC}"
        # 続行はしない（認証フローが完全に成功していない）
        exit 1
    fi

    # 結果サマリー
    print_header "テスト結果サマリー"
    echo -e "  総テスト数: ${TOTAL_TESTS}"
    echo -e "  ${GREEN}成功: ${PASSED_TESTS}${NC}"
    echo -e "  ${RED}失敗: ${FAILED_TESTS}${NC}"
    echo ""

    if [ "$FAILED_TESTS" -eq 0 ]; then
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}✓ 全てのE2Eテストが成功しました！${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "認証フローが正常に動作しています:"
        echo "  1. ユーザー登録 ✓"
        echo "  2. ログイン（JWT発行） ✓"
        echo "  3. 認証付きAPI呼び出し ✓"
        echo ""
        exit 0
    else
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${RED}✗ テスト失敗: ${FAILED_TESTS}個のテストが失敗しました${NC}"
        echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        exit 1
    fi
}

# スクリプト実行
main

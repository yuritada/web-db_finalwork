#!/usr/bin/env bash
###############################################################################
# Phase 2-3 API統合テストスクリプト
#
# 機能: Phase 2 (Wiki) と Phase 3 (タグ・検索) の統合テスト
# テストシナリオ:
#   1. 認証（ユーザー登録・ログイン）
#   2. Wiki機能（作成・一覧・詳細・更新・共有）
#   3. タグ機能（作成・一覧・詳細・割り当て・削除）
#   4. 検索機能（Wiki・タグ・ユーザー・統合検索）
#
# 使用方法:
#   bash backend/scripts/phase2_3_test.sh
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
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# テストユーザーデータ（ユニーク性確保のためタイムスタンプ使用）
TIMESTAMP=$(date +%s)
USER1_NAME="phase2_3_user1_${TIMESTAMP}"
USER1_EMAIL="user1_${TIMESTAMP}@example.com"
USER1_PASSWORD="TestPass123!"

USER2_NAME="phase2_3_user2_${TIMESTAMP}"
USER2_EMAIL="user2_${TIMESTAMP}@example.com"
USER2_PASSWORD="TestPass456!"

# 一時ファイル
RESPONSE_FILE=$(mktemp)
trap "rm -f ${RESPONSE_FILE}" EXIT

# テスト結果カウンター
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# グローバル変数（テスト間でデータを共有）
USER1_TOKEN=""
USER1_ID=""
USER2_TOKEN=""
USER2_ID=""
WIKI_PAGE_ID=""
TAG_ID=""

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

print_section() {
    echo ""
    echo -e "${CYAN}>>> $1${NC}"
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
# Phase 1: 認証テスト
###############################################################################

test_signup_user1() {
    print_step "ユーザー1登録: POST ${BASE_URL}/auth/signup"
    ((TOTAL_TESTS++))

    REQUEST_BODY=$(cat <<EOF
{
  "username": "${USER1_NAME}",
  "email": "${USER1_EMAIL}",
  "password": "${USER1_PASSWORD}",
  "kategori": "学生",
  "gakuseki_bango": "P2U${TIMESTAMP:(-6)}",
  "faculty": "工学部"
}
EOF
)

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X POST "${BASE_URL}/auth/signup" \
        -H "Content-Type: application/json" \
        -d "$REQUEST_BODY")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 201 ]; then
        print_success "ユーザー1登録成功 (HTTP $HTTP_CODE)"
        if check_jq; then
            USER1_ID=$(echo "$RESPONSE" | jq -r '.id')
            print_info "ユーザー1 ID: $USER1_ID"
        fi
        return 0
    else
        print_error "ユーザー1登録失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_login_user1() {
    print_step "ユーザー1ログイン: POST ${BASE_URL}/auth/token"
    ((TOTAL_TESTS++))

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X POST "${BASE_URL}/auth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=${USER1_NAME}&password=${USER1_PASSWORD}")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "ユーザー1ログイン成功 (HTTP $HTTP_CODE)"
        if check_jq; then
            USER1_TOKEN=$(echo "$RESPONSE" | jq -r '.access_token')
            print_info "トークン取得: ${USER1_TOKEN:0:20}..."
        else
            USER1_TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"\(.*\)"/\1/')
        fi
        return 0
    else
        print_error "ユーザー1ログイン失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_signup_user2() {
    print_step "ユーザー2登録: POST ${BASE_URL}/auth/signup"
    ((TOTAL_TESTS++))

    REQUEST_BODY=$(cat <<EOF
{
  "username": "${USER2_NAME}",
  "email": "${USER2_EMAIL}",
  "password": "${USER2_PASSWORD}",
  "kategori": "教授",
  "gakuseki_bango": null,
  "faculty": "情報工学科"
}
EOF
)

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X POST "${BASE_URL}/auth/signup" \
        -H "Content-Type: application/json" \
        -d "$REQUEST_BODY")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 201 ]; then
        print_success "ユーザー2登録成功 (HTTP $HTTP_CODE)"
        if check_jq; then
            USER2_ID=$(echo "$RESPONSE" | jq -r '.id')
            print_info "ユーザー2 ID: $USER2_ID"
        fi
        return 0
    else
        print_error "ユーザー2登録失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_login_user2() {
    print_step "ユーザー2ログイン: POST ${BASE_URL}/auth/token"
    ((TOTAL_TESTS++))

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X POST "${BASE_URL}/auth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=${USER2_NAME}&password=${USER2_PASSWORD}")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "ユーザー2ログイン成功 (HTTP $HTTP_CODE)"
        if check_jq; then
            USER2_TOKEN=$(echo "$RESPONSE" | jq -r '.access_token')
            print_info "トークン取得: ${USER2_TOKEN:0:20}..."
        else
            USER2_TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*"' | sed 's/"access_token":"\(.*\)"/\1/')
        fi
        return 0
    else
        print_error "ユーザー2ログイン失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

###############################################################################
# Phase 2: Wiki機能テスト
###############################################################################

test_create_wiki_page() {
    print_step "Wikiページ作成: POST ${BASE_URL}/wiki/pages"
    ((TOTAL_TESTS++))

    REQUEST_BODY=$(cat <<EOF
{
  "title": "テストWikiページ ${TIMESTAMP}",
  "content": "これはPhase 2統合テスト用のWikiページです。タイムスタンプ: ${TIMESTAMP}"
}
EOF
)

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X POST "${BASE_URL}/wiki/pages" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${USER1_TOKEN}" \
        -d "$REQUEST_BODY")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 201 ]; then
        print_success "Wikiページ作成成功 (HTTP $HTTP_CODE)"
        if check_jq; then
            WIKI_PAGE_ID=$(echo "$RESPONSE" | jq -r '.id')
            WIKI_TITLE=$(echo "$RESPONSE" | jq -r '.title')
            print_info "ページID: $WIKI_PAGE_ID"
            print_info "タイトル: $WIKI_TITLE"
        fi
        return 0
    else
        print_error "Wikiページ作成失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_get_wiki_pages() {
    print_step "Wikiページ一覧取得: GET ${BASE_URL}/wiki/pages"
    ((TOTAL_TESTS++))

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X GET "${BASE_URL}/wiki/pages" \
        -H "Authorization: Bearer ${USER1_TOKEN}")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "Wikiページ一覧取得成功 (HTTP $HTTP_CODE)"
        if check_jq; then
            PAGE_COUNT=$(echo "$RESPONSE" | jq '. | length')
            print_info "取得ページ数: $PAGE_COUNT"
        fi
        return 0
    else
        print_error "Wikiページ一覧取得失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_get_wiki_page_detail() {
    print_step "Wikiページ詳細取得: GET ${BASE_URL}/wiki/pages/${WIKI_PAGE_ID}"
    ((TOTAL_TESTS++))

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X GET "${BASE_URL}/wiki/pages/${WIKI_PAGE_ID}" \
        -H "Authorization: Bearer ${USER1_TOKEN}")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "Wikiページ詳細取得成功 (HTTP $HTTP_CODE)"
        if check_jq; then
            TITLE=$(echo "$RESPONSE" | jq -r '.title')
            print_info "タイトル: $TITLE"
        fi
        return 0
    else
        print_error "Wikiページ詳細取得失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_update_wiki_page() {
    print_step "Wikiページ更新: PUT ${BASE_URL}/wiki/pages/${WIKI_PAGE_ID}"
    ((TOTAL_TESTS++))

    REQUEST_BODY=$(cat <<EOF
{
  "title": "更新されたWikiページ ${TIMESTAMP}",
  "content": "内容が更新されました。更新時刻: $(date +%Y-%m-%d\ %H:%M:%S)"
}
EOF
)

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X PUT "${BASE_URL}/wiki/pages/${WIKI_PAGE_ID}" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${USER1_TOKEN}" \
        -d "$REQUEST_BODY")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "Wikiページ更新成功 (HTTP $HTTP_CODE)"
        if check_jq; then
            UPDATED_TITLE=$(echo "$RESPONSE" | jq -r '.title')
            print_info "新タイトル: $UPDATED_TITLE"
        fi
        return 0
    else
        print_error "Wikiページ更新失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_share_wiki_page() {
    print_step "Wikiページ共有: POST ${BASE_URL}/wiki/pages/${WIKI_PAGE_ID}/share"
    ((TOTAL_TESTS++))

    REQUEST_BODY=$(cat <<EOF
{
  "user_id": "${USER2_ID}",
  "permission_level": "VIEW_ONLY"
}
EOF
)

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X POST "${BASE_URL}/wiki/pages/${WIKI_PAGE_ID}/share" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${USER1_TOKEN}" \
        -d "$REQUEST_BODY")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 201 ]; then
        print_success "Wikiページ共有成功 (HTTP $HTTP_CODE)"
        print_info "ユーザー2にVIEW_ONLY権限を付与"
        return 0
    else
        print_error "Wikiページ共有失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_user2_view_wiki() {
    print_step "ユーザー2でWikiページ閲覧: GET ${BASE_URL}/wiki/pages/${WIKI_PAGE_ID}"
    ((TOTAL_TESTS++))

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X GET "${BASE_URL}/wiki/pages/${WIKI_PAGE_ID}" \
        -H "Authorization: Bearer ${USER2_TOKEN}")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "ユーザー2でWikiページ閲覧成功 (HTTP $HTTP_CODE)"
        print_info "権限共有が正常に動作"
        return 0
    else
        print_error "ユーザー2でWikiページ閲覧失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

###############################################################################
# Phase 3: タグ機能テスト
###############################################################################

test_create_tag() {
    print_step "タグ作成: POST ${BASE_URL}/tags"
    ((TOTAL_TESTS++))

    REQUEST_BODY=$(cat <<EOF
{
  "name": "Phase2-3テスト_${TIMESTAMP}"
}
EOF
)

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X POST "${BASE_URL}/tags" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${USER1_TOKEN}" \
        -d "$REQUEST_BODY")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 201 ]; then
        print_success "タグ作成成功 (HTTP $HTTP_CODE)"
        if check_jq; then
            TAG_ID=$(echo "$RESPONSE" | jq -r '.id')
            TAG_NAME=$(echo "$RESPONSE" | jq -r '.name')
            print_info "タグID: $TAG_ID"
            print_info "タグ名: $TAG_NAME"
        fi
        return 0
    else
        print_error "タグ作成失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_get_tags() {
    print_step "タグ一覧取得: GET ${BASE_URL}/tags"
    ((TOTAL_TESTS++))

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X GET "${BASE_URL}/tags" \
        -H "Authorization: Bearer ${USER1_TOKEN}")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "タグ一覧取得成功 (HTTP $HTTP_CODE)"
        if check_jq; then
            TAG_COUNT=$(echo "$RESPONSE" | jq '. | length')
            print_info "取得タグ数: $TAG_COUNT"
        fi
        return 0
    else
        print_error "タグ一覧取得失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_get_tag_detail() {
    print_step "タグ詳細取得: GET ${BASE_URL}/tags/${TAG_ID}"
    ((TOTAL_TESTS++))

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X GET "${BASE_URL}/tags/${TAG_ID}" \
        -H "Authorization: Bearer ${USER1_TOKEN}")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "タグ詳細取得成功 (HTTP $HTTP_CODE)"
        if check_jq; then
            NAME=$(echo "$RESPONSE" | jq -r '.name')
            print_info "タグ名: $NAME"
        fi
        return 0
    else
        print_error "タグ詳細取得失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_assign_tag() {
    print_step "タグ割り当て: POST ${BASE_URL}/tags/${TAG_ID}/assign"
    ((TOTAL_TESTS++))

    REQUEST_BODY=$(cat <<EOF
{
  "user_id": "${USER2_ID}"
}
EOF
)

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X POST "${BASE_URL}/tags/${TAG_ID}/assign" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${USER1_TOKEN}" \
        -d "$REQUEST_BODY")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 201 ]; then
        print_success "タグ割り当て成功 (HTTP $HTTP_CODE)"
        print_info "ユーザー2にタグを付与"
        return 0
    else
        print_error "タグ割り当て失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

###############################################################################
# Phase 3: 検索機能テスト
###############################################################################

test_search_wiki() {
    print_step "Wiki検索: GET ${BASE_URL}/search?q=テスト&type=wiki"
    ((TOTAL_TESTS++))

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X GET "${BASE_URL}/search?q=%E3%83%86%E3%82%B9%E3%83%88&type=wiki" \
        -H "Authorization: Bearer ${USER1_TOKEN}")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "Wiki検索成功 (HTTP $HTTP_CODE)"
        if check_jq; then
            RESULT_COUNT=$(echo "$RESPONSE" | jq '.total')
            print_info "検索結果数: $RESULT_COUNT"
        fi
        return 0
    else
        print_error "Wiki検索失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_search_tags() {
    print_step "タグ検索: GET ${BASE_URL}/search?q=Phase2&type=tag"
    ((TOTAL_TESTS++))

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X GET "${BASE_URL}/search?q=Phase2&type=tag" \
        -H "Authorization: Bearer ${USER1_TOKEN}")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "タグ検索成功 (HTTP $HTTP_CODE)"
        if check_jq; then
            RESULT_COUNT=$(echo "$RESPONSE" | jq '.total')
            print_info "検索結果数: $RESULT_COUNT"
        fi
        return 0
    else
        print_error "タグ検索失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_search_users() {
    print_step "ユーザー検索: GET ${BASE_URL}/search?q=phase2_3&type=user"
    ((TOTAL_TESTS++))

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X GET "${BASE_URL}/search?q=phase2_3&type=user" \
        -H "Authorization: Bearer ${USER1_TOKEN}")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "ユーザー検索成功 (HTTP $HTTP_CODE)"
        if check_jq; then
            RESULT_COUNT=$(echo "$RESPONSE" | jq '.total')
            print_info "検索結果数: $RESULT_COUNT"
        fi
        return 0
    else
        print_error "ユーザー検索失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

test_search_all() {
    print_step "統合検索: GET ${BASE_URL}/search?q=${TIMESTAMP}&type=all"
    ((TOTAL_TESTS++))

    HTTP_CODE=$(curl -s -o "${RESPONSE_FILE}" -w "%{http_code}" \
        -X GET "${BASE_URL}/search?q=${TIMESTAMP}&type=all" \
        -H "Authorization: Bearer ${USER1_TOKEN}")

    RESPONSE=$(cat "${RESPONSE_FILE}")

    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "統合検索成功 (HTTP $HTTP_CODE)"
        if check_jq; then
            RESULT_COUNT=$(echo "$RESPONSE" | jq '.total')
            print_info "全体検索結果数: $RESULT_COUNT"
        fi
        return 0
    else
        print_error "統合検索失敗 (HTTP $HTTP_CODE)"
        print_info "レスポンス: $RESPONSE"
        return 1
    fi
}

###############################################################################
# メイン実行
###############################################################################

main() {
    print_header "Phase 2-3 API統合テスト開始"

    echo "テスト設定:"
    echo "  - API Base URL: $BASE_URL"
    echo "  - タイムスタンプ: $TIMESTAMP"
    echo "  - jq利用可能: $(check_jq && echo 'Yes' || echo 'No')"
    echo ""

    # Phase 1: 認証
    print_section "Phase 1: 認証テスト"
    test_signup_user1 || exit 1
    test_login_user1 || exit 1
    test_signup_user2 || exit 1
    test_login_user2 || exit 1

    # Phase 2: Wiki機能
    print_section "Phase 2: Wiki機能テスト"
    test_create_wiki_page || exit 1
    test_get_wiki_pages || exit 1
    test_get_wiki_page_detail || exit 1
    test_update_wiki_page || exit 1
    test_share_wiki_page || exit 1
    test_user2_view_wiki || exit 1

    # Phase 3: タグ機能
    print_section "Phase 3: タグ機能テスト"
    test_create_tag || exit 1
    test_get_tags || exit 1
    test_get_tag_detail || exit 1
    test_assign_tag || exit 1

    # Phase 3: 検索機能
    print_section "Phase 3: 検索機能テスト"
    test_search_wiki || exit 1
    test_search_tags || exit 1
    test_search_users || exit 1
    test_search_all || exit 1

    # 結果サマリー
    print_header "テスト結果サマリー"
    echo -e "  総テスト数: ${TOTAL_TESTS}"
    echo -e "  ${GREEN}成功: ${PASSED_TESTS}${NC}"
    echo -e "  ${RED}失敗: ${FAILED_TESTS}${NC}"
    echo ""

    if [ "$FAILED_TESTS" -eq 0 ]; then
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${GREEN}✓ 全てのPhase 2-3統合テストが成功しました！${NC}"
        echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        echo "Phase 2-3 API実装が正常に動作しています:"
        echo "  Phase 1: 認証 ✓"
        echo "  Phase 2: Wiki機能（作成・一覧・詳細・更新・共有）✓"
        echo "  Phase 3: タグ機能（作成・一覧・詳細・割り当て）✓"
        echo "  Phase 3: 検索機能（Wiki・タグ・ユーザー・統合）✓"
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

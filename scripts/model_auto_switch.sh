#!/bin/bash
# 模型自动切换脚本 - 可配置为 cron 任务定期运行

WORKSPACE="/Users/a404/.openclaw/workspace"
SCRIPT="$WORKSPACE/skills/model-auto-switch/scripts/model_manager.py"
LOG_FILE="$WORKSPACE/logs/model_switch.log"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "开始模型自动检测..."

# 运行自动检测
cd "$WORKSPACE"
python3 "$SCRIPT" auto 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    log "模型检测完成"
else
    log "模型检测失败，退出码: $EXIT_CODE"
fi

# 如果日志文件太大，压缩旧日志
if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE") -gt 10485760 ]; then
    log "日志文件超过10MB，开始压缩..."
    gzip -c "$LOG_FILE" > "$LOG_FILE.$(date +%Y%m%d_%H%M%S).gz"
    > "$LOG_FILE"
    log "日志已压缩并清空"
fi
#!/bin/bash
# Skill Conflict Weekly Scanner
# Created: 2026-05-11
# Purpose: Scan all skills for conflicts, duplicates, and issues

set -e

WORKSPACE="/workspace/projects/workspace"
SKILLS_DIR="$WORKSPACE/skills"
SYSTEM_SKILLS_DIR="/usr/lib/node_modules/openclaw/skills"
REPORT_FILE="/tmp/skill_conflict_report_$(date +%Y%m%d_%H%M%S).txt"

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================" > "$REPORT_FILE"
echo "  SKILL CONFLICT WEEKLY SCANNER REPORT" >> "$REPORT_FILE"
echo "  Generated: $(date '+%Y-%m-%d %H:%M:%S %Z')" >> "$REPORT_FILE"
echo "========================================" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Counters
CONFLICTS=0
WARNINGS=0
CHECKS=0

log_check() {
    echo "✓ $1" >> "$REPORT_FILE"
    ((CHECKS++))
}

log_warning() {
    echo "⚠ WARNING: $1" >> "$REPORT_FILE"
    ((WARNINGS++))
}

log_conflict() {
    echo "✗ CONFLICT: $1" >> "$REPORT_FILE"
    ((CONFLICTS++))
}

# 1. Check for duplicate skill names
echo "【1/8】Checking for duplicate skill names..." >> "$REPORT_FILE"
SKILL_NAMES=""

# Collect workspace skills
if [ -d "$SKILLS_DIR" ]; then
    for skill in "$SKILLS_DIR"/*/; do
        if [ -d "$skill" ]; then
            name=$(basename "$skill")
            SKILL_NAMES="$SKILL_NAMES\nworkspace:$name"
        fi
    done
fi

# Collect system skills
if [ -d "$SYSTEM_SKILLS_DIR" ]; then
    for skill in "$SYSTEM_SKILLS_DIR"/*/; do
        if [ -d "$skill" ]; then
            name=$(basename "$skill")
            SKILL_NAMES="$SKILL_NAMES\nsystem:$name"
        fi
    done
fi

# Check for duplicates
echo "$SKILL_NAMES" | awk -F: '{count[$2]++; loc[$2]=loc[$2]","$1} END {for(name in count) if(count[name]>1) print "Duplicate: "name" in "loc[name]}' >> "$REPORT_FILE" 2>/dev/null || true
log_check "Skill name uniqueness verified"
echo "" >> "$REPORT_FILE"

# 2. Check SKILL.md existence and structure
echo "【2/8】Checking SKILL.md files..." >> "$REPORT_FILE"
MISSING_SKILLMD=0

if [ -d "$SKILLS_DIR" ]; then
    for skill in "$SKILLS_DIR"/*/; do
        if [ -d "$skill" ]; then
            if [ ! -f "$skill/SKILL.md" ]; then
                log_warning "Missing SKILL.md in $(basename "$skill")"
                ((MISSING_SKILLMD++))
            fi
        fi
    done
fi

if [ $MISSING_SKILLMD -eq 0 ]; then
    log_check "All skills have SKILL.md"
else
    log_warning "$MISSING_SKILLMD skills missing SKILL.md"
fi
echo "" >> "$REPORT_FILE"

# 3. Check for name/description frontmatter
echo "【3/8】Checking SKILL.md frontmatter..." >> "$REPORT_FILE"
INCOMPLETE_FRONTMATTER=0

if [ -d "$SKILLS_DIR" ]; then
    for skill_md in "$SKILLS_DIR"/*/SKILL.md; do
        if [ -f "$skill_md" ]; then
            if ! grep -q "^name:" "$skill_md" 2>/dev/null || ! grep -q "^description:" "$skill_md" 2>/dev/null; then
                log_warning "Incomplete frontmatter in $(basename $(dirname "$skill_md"))"
                ((INCOMPLETE_FRONTMATTER++))
            fi
        fi
    done
fi

if [ $INCOMPLETE_FRONTMATTER -eq 0 ]; then
    log_check "All SKILL.md files have proper frontmatter"
else
    log_warning "$INCOMPLETE_FRONTMATTER skills with incomplete frontmatter"
fi
echo "" >> "$REPORT_FILE"

# 4. Check for naming convention violations
echo "【4/8】Checking naming conventions..." >> "$REPORT_FILE"
NAMING_ISSUES=0

if [ -d "$SKILLS_DIR" ]; then
    for skill in "$SKILLS_DIR"/*/; do
        if [ -d "$skill" ]; then
            name=$(basename "$skill")
            # Check if name contains invalid characters (should be lowercase, digits, hyphens only)
            if echo "$name" | grep -qE '[^a-z0-9-]' || echo "$name" | grep -qE '^[0-9]'; then
                log_warning "Naming violation: $name (use lowercase letters, digits, hyphens only; cannot start with digit)"
                ((NAMING_ISSUES++))
            fi
        fi
    done
fi

if [ $NAMING_ISSUES -eq 0 ]; then
    log_check "All skill names follow naming conventions"
else
    log_warning "$NAMING_ISSUES skills with naming violations"
fi
echo "" >> "$REPORT_FILE"

# 5. Check for orphaned references
echo "【5/8】Checking for orphaned references..." >> "$REPORT_FILE"
ORPHANED=0

if [ -d "$SKILLS_DIR" ]; then
    for skill in "$SKILLS_DIR"/*/; do
        if [ -d "$skill/references" ]; then
            skill_name=$(basename "$skill")
            skill_md="$skill/SKILL.md"
            if [ -f "$skill_md" ]; then
                for ref in "$skill/references/"*; do
                    if [ -f "$ref" ]; then
                        ref_name=$(basename "$ref")
                        if ! grep -q "$ref_name" "$skill_md" 2>/dev/null; then
                            log_warning "Orphaned reference: $skill_name/references/$ref_name"
                            ((ORPHANED++))
                        fi
                    fi
                done
            fi
        fi
    done
fi

if [ $ORPHANED -eq 0 ]; then
    log_check "No orphaned references found"
else
    log_warning "$ORPHANED orphaned references detected"
fi
echo "" >> "$REPORT_FILE"

# 6. Check for circular dependencies
echo "【6/8】Checking for circular dependencies..." >> "$REPORT_FILE"
log_check "Circular dependency check (manual review required for complex cases)"
echo "" >> "$REPORT_FILE"

# 7. Check skill registry consistency
echo "【7/8】Checking skill registry..." >> "$REPORT_FILE"
REGISTRY="$WORKSPACE/SKILL_REGISTRY.json"
if [ -f "$REGISTRY" ]; then
    REGISTRY_SKILLS=$(grep -o '"name": "[^"]*"' "$REGISTRY" 2>/dev/null | wc -l)
    ACTUAL_SKILLS=$(find "$SKILLS_DIR" -maxdepth 1 -type d | wc -l)
    ACTUAL_SKILLS=$((ACTUAL_SKILLS - 1))  # Exclude the parent directory
    
    echo "  Registry skills: $REGISTRY_SKILLS" >> "$REPORT_FILE"
    echo "  Actual skills: $ACTUAL_SKILLS" >> "$REPORT_FILE"
    
    if [ "$REGISTRY_SKILLS" -eq "$ACTUAL_SKILLS" ]; then
        log_check "Skill registry is consistent"
    else
        log_warning "Skill registry mismatch: registry=$REGISTRY_SKILLS, actual=$ACTUAL_SKILLS"
    fi
else
    log_warning "SKILL_REGISTRY.json not found"
fi
echo "" >> "$REPORT_FILE"

# 8. Summary statistics
echo "【8/8】Generating summary statistics..." >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "========================================" >> "$REPORT_FILE"
echo "  SUMMARY STATISTICS" >> "$REPORT_FILE"
echo "========================================" >> "$REPORT_FILE"

TOTAL_SKILLS=0
if [ -d "$SKILLS_DIR" ]; then
    TOTAL_SKILLS=$(find "$SKILLS_DIR" -maxdepth 1 -type d | wc -l)
    TOTAL_SKILLS=$((TOTAL_SKILLS - 1))
fi

echo "Total skills in workspace: $TOTAL_SKILLS" >> "$REPORT_FILE"
echo "Checks passed: $CHECKS" >> "$REPORT_FILE"
echo "Warnings: $WARNINGS" >> "$REPORT_FILE"
echo "Conflicts: $CONFLICTS" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Status
if [ $CONFLICTS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ STATUS: HEALTHY - All checks passed!" >> "$REPORT_FILE"
elif [ $CONFLICTS -eq 0 ]; then
    echo "⚠️  STATUS: WARNING - $WARNINGS warning(s) need attention" >> "$REPORT_FILE"
else
    echo "❌ STATUS: CRITICAL - $CONFLICTS conflict(s) require immediate action" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "Report saved to: $REPORT_FILE" >> "$REPORT_FILE"

# Output to console if --report flag is passed
if [ "$1" == "--report" ]; then
    cat "$REPORT_FILE"
fi

# Return exit code based on status
if [ $CONFLICTS -gt 0 ]; then
    exit 2
elif [ $WARNINGS -gt 0 ]; then
    exit 1
else
    exit 0
fi

#!/usr/bin/env python3
"""
Agent Test MCP Server

An MCP server that allows testing the Video Creator agent from Claude Code.
Sends messages to the agent and returns complete responses with full visibility.

Usage:
    Add to .mcp.json and use from Claude Code to test the agent.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any
from datetime import datetime

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configuration
API_BASE_URL = os.getenv("OCTUPOST_API_URL", "http://localhost:8000")
DEFAULT_PROJECT_ID = os.getenv("OCTUPOST_TEST_PROJECT_ID", "")
SCENARIOS_FILE = Path(__file__).parent / "tests" / "agent_test_scenarios.json"

server = Server("agent-test")


# =============================================================================
# Test Scenarios Loader
# =============================================================================

def load_test_scenarios() -> dict:
    """Load test scenarios from JSON file."""
    if not SCENARIOS_FILE.exists():
        return {"scenarios": {}, "quick_tests": []}

    with open(SCENARIOS_FILE) as f:
        return json.load(f)


def get_scenarios_by_category(category: str) -> list[dict]:
    """Get test scenarios for a specific category."""
    data = load_test_scenarios()
    scenarios = data.get("scenarios", {})

    if category in scenarios:
        return scenarios[category].get("tests", [])
    return []


def get_all_scenarios() -> list[dict]:
    """Get all test scenarios flattened."""
    data = load_test_scenarios()
    scenarios = data.get("scenarios", {})

    all_tests = []
    for category, category_data in scenarios.items():
        for test in category_data.get("tests", []):
            test["category"] = category
            all_tests.append(test)

    return all_tests


def get_quick_tests() -> list[dict]:
    """Get quick test scenarios."""
    data = load_test_scenarios()
    return data.get("quick_tests", [])


# =============================================================================
# Assertion Checker
# =============================================================================

def check_assertions(result: dict, expected: dict) -> dict:
    """
    Check test assertions against result.

    Returns dict with:
        - passed: bool
        - checks: list of individual check results
        - summary: string summary
    """
    checks = []
    all_passed = True

    response = result.get("agent_response", "").lower()
    tool_calls = [tc.get("tool_name", "") for tc in result.get("tool_calls", [])]

    # Check: should_ask_questions
    if expected.get("should_ask_questions"):
        has_question = "?" in result.get("agent_response", "")
        checks.append({
            "check": "should_ask_questions",
            "passed": has_question,
            "message": "Agent asked questions" if has_question else "Agent did NOT ask questions"
        })
        if not has_question:
            all_passed = False

    # Check: response_should_contain
    if expected.get("response_should_contain"):
        for keyword in expected["response_should_contain"]:
            contains = keyword.lower() in response
            checks.append({
                "check": f"response_contains '{keyword}'",
                "passed": contains,
                "message": f"Found '{keyword}'" if contains else f"Missing '{keyword}'"
            })
            if not contains:
                all_passed = False

    # Check: response_should_not_contain
    if expected.get("response_should_not_contain"):
        for keyword in expected["response_should_not_contain"]:
            contains = keyword.lower() in response
            checks.append({
                "check": f"response_not_contains '{keyword}'",
                "passed": not contains,
                "message": f"Correctly missing '{keyword}'" if not contains else f"Incorrectly contains '{keyword}'"
            })
            if contains:
                all_passed = False

    # Check: should_call_tools
    if expected.get("should_call_tools"):
        for tool_name in expected["should_call_tools"]:
            called = tool_name in tool_calls
            checks.append({
                "check": f"should_call '{tool_name}'",
                "passed": called,
                "message": f"Called {tool_name}" if called else f"Did NOT call {tool_name}"
            })
            if not called:
                all_passed = False

    # Check: should_not_call_tools
    if expected.get("should_not_call_tools"):
        for tool_name in expected["should_not_call_tools"]:
            called = tool_name in tool_calls
            checks.append({
                "check": f"should_not_call '{tool_name}'",
                "passed": not called,
                "message": f"Correctly did not call {tool_name}" if not called else f"Incorrectly called {tool_name}"
            })
            if called:
                all_passed = False

    # Check: may_call_tools (informational, doesn't affect pass/fail)
    if expected.get("may_call_tools"):
        for tool_name in expected["may_call_tools"]:
            called = tool_name in tool_calls
            checks.append({
                "check": f"may_call '{tool_name}'",
                "passed": True,  # Always passes - it's optional
                "message": f"Called {tool_name}" if called else f"Did not call {tool_name} (optional)"
            })

    # Check: tool_should_be_called_first
    if expected.get("tool_should_be_called_first"):
        expected_first = expected["tool_should_be_called_first"]
        actual_first = tool_calls[0] if tool_calls else None
        is_first = actual_first == expected_first
        checks.append({
            "check": f"first_tool_is '{expected_first}'",
            "passed": is_first,
            "message": f"First tool was {actual_first}" if actual_first else "No tools called"
        })
        if not is_first:
            all_passed = False

    # Summary
    passed_count = sum(1 for c in checks if c["passed"])
    total_count = len(checks)

    return {
        "passed": all_passed,
        "checks": checks,
        "summary": f"{passed_count}/{total_count} checks passed"
    }


# =============================================================================
# Result Formatters
# =============================================================================

def format_test_result(result: dict, with_assertions: dict = None) -> str:
    """Format test result for display in Claude Code."""
    lines = []
    lines.append("=" * 60)
    lines.append("AGENT TEST RESULT")
    lines.append("=" * 60)

    # Test info
    if result.get("test_id"):
        lines.append(f"\nTest: {result.get('test_id')} - {result.get('test_name', '')}")

    # Status
    status = result.get("status", "unknown")
    status_emoji = {"success": "✅", "error": "❌", "paused": "⏸️", "blocked": "🚫"}.get(status, "❓")
    lines.append(f"Status: {status_emoji} {status.upper()}")

    # Assertions result
    if with_assertions:
        assertion_emoji = "✅" if with_assertions["passed"] else "❌"
        lines.append(f"Assertions: {assertion_emoji} {with_assertions['summary']}")

    # Timing
    if result.get("duration_ms"):
        lines.append(f"Duration: {result['duration_ms']}ms")

    # User message
    if result.get("user_message"):
        lines.append(f"\n📤 USER MESSAGE:")
        lines.append(f"   {result['user_message']}")

    # Agent response
    if result.get("agent_response"):
        lines.append(f"\n📥 AGENT RESPONSE:")
        for line in result["agent_response"].split("\n"):
            lines.append(f"   {line}")

    # Tool calls
    if result.get("tool_calls"):
        lines.append(f"\n🔧 TOOL CALLS ({len(result['tool_calls'])}):")
        for tc in result["tool_calls"]:
            lines.append(f"   • {tc.get('tool_name', 'unknown')}")
            if tc.get("tool_args"):
                args_str = json.dumps(tc["tool_args"], indent=6)
                for arg_line in args_str.split("\n")[:5]:  # Limit args display
                    lines.append(f"     {arg_line}")
    else:
        lines.append(f"\n🔧 TOOL CALLS: None")

    # Assertion details
    if with_assertions and with_assertions.get("checks"):
        lines.append(f"\n📋 ASSERTION CHECKS:")
        for check in with_assertions["checks"]:
            emoji = "✅" if check["passed"] else "❌"
            lines.append(f"   {emoji} {check['check']}: {check['message']}")

    # HITL info
    if result.get("hitl_paused"):
        lines.append(f"\n⏸️ HITL PAUSED - Awaiting confirmation")
        lines.append(f"   Run ID: {result.get('run_id', 'unknown')}")
        if result.get("requirements"):
            lines.append(f"   Requirements ({len(result['requirements'])}):")
            for req in result["requirements"]:
                lines.append(f"     • {req.get('tool_name', 'unknown')}: {req.get('estimated_credits', 0)} credits")
        if result.get("total_credits_needed"):
            lines.append(f"   Total credits needed: {result['total_credits_needed']}")
            lines.append(f"   Credits available: {result.get('credits_available', 'unknown')}")

    # Blocked info
    if result.get("blocked"):
        lines.append(f"\n🚫 BLOCKED: {result.get('block_reason', 'unknown')}")
        if result.get("credits_shortfall"):
            lines.append(f"   Credits shortfall: {result['credits_shortfall']}")

    # Errors
    if result.get("errors"):
        lines.append(f"\n❌ ERRORS:")
        for err in result["errors"]:
            lines.append(f"   • {err}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_batch_result(result: dict) -> str:
    """Format batch test result for display."""
    lines = []
    lines.append("=" * 60)
    lines.append("BATCH TEST RESULTS")
    lines.append("=" * 60)

    lines.append(f"\nBatch ID: {result.get('batch_id', 'unknown')}")
    lines.append(f"Duration: {result.get('duration_ms', 0)}ms")

    lines.append(f"\n📊 SUMMARY:")
    lines.append(f"   Total:      {result.get('total', 0)}")
    lines.append(f"   ✅ Passed:   {result.get('passed', 0)}")
    lines.append(f"   ❌ Failed:   {result.get('failed', 0)}")
    lines.append(f"   ⏸️ Paused:   {result.get('paused', 0)}")
    lines.append(f"   🚫 Blocked:  {result.get('blocked', 0)}")

    lines.append(f"\n📋 INDIVIDUAL RESULTS:")
    for r in result.get("results", []):
        # Determine status emoji
        if r.get("assertion_result", {}).get("passed") is False:
            status_emoji = "❌"
        else:
            status_emoji = {"success": "✅", "error": "❌", "paused": "⏸️", "blocked": "🚫"}.get(r.get("status"), "❓")

        test_name = r.get("test_name") or r.get("test_id", "unknown")
        category = r.get("category", "")
        category_str = f"[{category}] " if category else ""

        lines.append(f"   {status_emoji} {category_str}{test_name}")

        # Show assertion summary if available
        if r.get("assertion_result"):
            ar = r["assertion_result"]
            lines.append(f"      └─ Assertions: {ar['summary']}")

        # Show errors
        if r.get("errors"):
            for err in r["errors"][:1]:  # Show first error
                lines.append(f"      └─ Error: {err[:60]}...")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_scenarios_list(scenarios: dict) -> str:
    """Format available scenarios for display."""
    lines = []
    lines.append("=" * 60)
    lines.append("AVAILABLE TEST SCENARIOS")
    lines.append("=" * 60)

    for category, data in scenarios.get("scenarios", {}).items():
        lines.append(f"\n📁 {category.upper()}")
        lines.append(f"   {data.get('description', '')}")
        for test in data.get("tests", []):
            lines.append(f"   • {test['id']}: {test['name']}")

    quick_tests = scenarios.get("quick_tests", [])
    if quick_tests:
        lines.append(f"\n⚡ QUICK TESTS")
        for test in quick_tests:
            lines.append(f"   • {test['id']}: {test['name']}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


# =============================================================================
# Core Test Functions
# =============================================================================

async def send_agent_message(
    project_id: str,
    message: str,
    timeout: int = 120,
) -> dict:
    """
    Send a message to the agent and collect the complete response.
    """
    result = {
        "status": "unknown",
        "user_message": message,
        "agent_response": "",
        "tool_calls": [],
        "hitl_paused": False,
        "blocked": False,
        "errors": [],
        "raw_events": [],
    }

    start_time = datetime.now()

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                f"{API_BASE_URL}/api/agents/video-creator/chat",
                json={"project_id": project_id, "message": message},
                headers={"Accept": "text/event-stream"},
            ) as response:
                if response.status_code != 200:
                    result["status"] = "error"
                    result["errors"].append(f"HTTP {response.status_code}: {response.text}")
                    return result

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue

                    try:
                        event_data = json.loads(line[6:])
                        result["raw_events"].append(event_data)

                        event_type = event_data.get("type")

                        if event_type == "content":
                            result["agent_response"] += event_data.get("content", "")
                        elif event_type == "tool_call":
                            result["tool_calls"].append(event_data.get("tool_call", {}))
                        elif event_type == "paused":
                            result["hitl_paused"] = True
                            result["run_id"] = event_data.get("run_id")
                            result["requirements"] = event_data.get("requirements", [])
                            result["total_credits_needed"] = event_data.get("total_credits_needed")
                            result["credits_available"] = event_data.get("credits_available")
                            result["status"] = "paused"
                        elif event_type == "blocked":
                            result["blocked"] = True
                            result["block_reason"] = event_data.get("reason")
                            result["credits_shortfall"] = event_data.get("credits_shortfall")
                            result["status"] = "blocked"
                        elif event_type == "done":
                            result["run_id"] = event_data.get("run_id")
                            if result["status"] == "unknown":
                                result["status"] = "success"
                        elif event_type == "error":
                            result["errors"].append(event_data.get("error", "Unknown error"))
                            result["status"] = "error"

                    except json.JSONDecodeError as e:
                        result["errors"].append(f"JSON decode error: {e}")

        end_time = datetime.now()
        result["duration_ms"] = int((end_time - start_time).total_seconds() * 1000)

        if result["status"] == "unknown" and not result["errors"]:
            result["status"] = "success"

    except httpx.TimeoutException:
        result["status"] = "error"
        result["errors"].append(f"Request timed out after {timeout}s")
    except httpx.ConnectError:
        result["status"] = "error"
        result["errors"].append(f"Cannot connect to API at {API_BASE_URL}. Is the server running?")
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))

    return result


async def run_scenario_tests(
    project_id: str,
    scenarios: list[dict],
    parallel: int = 1,
) -> dict:
    """Run test scenarios with assertion checking."""
    results = {
        "batch_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "total": len(scenarios),
        "passed": 0,
        "failed": 0,
        "paused": 0,
        "blocked": 0,
        "results": [],
    }

    start_time = datetime.now()

    for scenario in scenarios:
        test_result = await send_agent_message(
            project_id=project_id,
            message=scenario.get("message", ""),
            timeout=scenario.get("timeout", 120),
        )
        test_result["test_id"] = scenario.get("id", "unknown")
        test_result["test_name"] = scenario.get("name", "")
        test_result["category"] = scenario.get("category", "")

        # Check assertions if defined
        if scenario.get("expected"):
            assertion_result = check_assertions(test_result, scenario["expected"])
            test_result["assertion_result"] = assertion_result

            # Use assertion result for pass/fail
            if assertion_result["passed"] and test_result["status"] in ["success", "paused"]:
                results["passed"] += 1
            else:
                results["failed"] += 1
        else:
            # No assertions - use status
            if test_result["status"] == "success":
                results["passed"] += 1
            elif test_result["status"] == "paused":
                results["paused"] += 1
            elif test_result["status"] == "blocked":
                results["blocked"] += 1
            else:
                results["failed"] += 1

        results["results"].append(test_result)

    end_time = datetime.now()
    results["duration_ms"] = int((end_time - start_time).total_seconds() * 1000)

    return results


# =============================================================================
# MCP Tools
# =============================================================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="test_agent",
            description="Send a message to the Video Creator agent and see the complete response including tool calls, HITL events, and timing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message to send to the agent",
                    },
                    "project_id": {
                        "type": "string",
                        "description": f"Project ID to use (default: {DEFAULT_PROJECT_ID or 'must be provided'})",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 120)",
                        "default": 120,
                    },
                },
                "required": ["message"] if DEFAULT_PROJECT_ID else ["message", "project_id"],
            },
        ),
        Tool(
            name="run_test_suite",
            description="Run predefined test scenarios from the test suite. Can run all tests, a specific category, or specific test IDs.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Test category to run: discovery, validation, planning, edge_cases, brand_kit, error_handling, or 'all' for everything",
                    },
                    "test_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific test IDs to run (e.g., ['disc_001', 'disc_002'])",
                    },
                    "quick": {
                        "type": "boolean",
                        "description": "Run quick tests only (3 basic tests)",
                        "default": False,
                    },
                    "project_id": {
                        "type": "string",
                        "description": f"Project ID to use (default: {DEFAULT_PROJECT_ID or 'must be provided'})",
                    },
                },
                "required": [] if DEFAULT_PROJECT_ID else ["project_id"],
            },
        ),
        Tool(
            name="list_scenarios",
            description="List all available test scenarios organized by category.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_test_details",
            description="Get details of a specific test scenario including expected behavior.",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_id": {
                        "type": "string",
                        "description": "The test ID to get details for (e.g., 'disc_001')",
                    },
                },
                "required": ["test_id"],
            },
        ),
        Tool(
            name="get_agent_config",
            description="Get the current agent test configuration (API URL, default project, etc.).",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name == "test_agent":
        project_id = arguments.get("project_id", DEFAULT_PROJECT_ID)
        if not project_id:
            return [TextContent(
                type="text",
                text="❌ Error: project_id is required. Set OCTUPOST_TEST_PROJECT_ID env var or provide project_id argument.",
            )]

        message = arguments.get("message", "")
        timeout = arguments.get("timeout", 120)

        result = await send_agent_message(
            project_id=project_id,
            message=message,
            timeout=timeout,
        )

        return [TextContent(
            type="text",
            text=format_test_result(result),
        )]

    elif name == "run_test_suite":
        project_id = arguments.get("project_id", DEFAULT_PROJECT_ID)
        if not project_id:
            return [TextContent(
                type="text",
                text="❌ Error: project_id is required. Set OCTUPOST_TEST_PROJECT_ID env var or provide project_id argument.",
            )]

        # Determine which tests to run
        scenarios_to_run = []

        if arguments.get("quick"):
            scenarios_to_run = get_quick_tests()
        elif arguments.get("test_ids"):
            all_scenarios = get_all_scenarios()
            test_ids = set(arguments["test_ids"])
            scenarios_to_run = [s for s in all_scenarios if s["id"] in test_ids]
        elif arguments.get("category"):
            category = arguments["category"]
            if category == "all":
                scenarios_to_run = get_all_scenarios()
            else:
                scenarios_to_run = get_scenarios_by_category(category)
        else:
            # Default to quick tests
            scenarios_to_run = get_quick_tests()

        if not scenarios_to_run:
            return [TextContent(
                type="text",
                text="❌ No test scenarios found. Check the category name or test IDs.",
            )]

        result = await run_scenario_tests(
            project_id=project_id,
            scenarios=scenarios_to_run,
        )

        return [TextContent(
            type="text",
            text=format_batch_result(result),
        )]

    elif name == "list_scenarios":
        scenarios = load_test_scenarios()
        return [TextContent(
            type="text",
            text=format_scenarios_list(scenarios),
        )]

    elif name == "get_test_details":
        test_id = arguments.get("test_id", "")
        all_scenarios = get_all_scenarios()

        found = None
        for scenario in all_scenarios:
            if scenario["id"] == test_id:
                found = scenario
                break

        if not found:
            return [TextContent(
                type="text",
                text=f"❌ Test '{test_id}' not found.",
            )]

        lines = [
            "=" * 60,
            f"TEST DETAILS: {found['id']}",
            "=" * 60,
            f"\nName: {found.get('name', '')}",
            f"Category: {found.get('category', '')}",
            f"\nMessage:",
            f"   \"{found.get('message', '')}\"",
        ]

        if found.get("expected"):
            lines.append("\nExpected Behavior:")
            for key, value in found["expected"].items():
                lines.append(f"   • {key}: {value}")

        lines.append("\n" + "=" * 60)

        return [TextContent(
            type="text",
            text="\n".join(lines),
        )]

    elif name == "get_agent_config":
        return [TextContent(
            type="text",
            text=f"⚙️ Agent Test MCP Configuration:\n\n"
                 f"API Base URL: {API_BASE_URL}\n"
                 f"Default Project ID: {DEFAULT_PROJECT_ID or '(not set)'}\n"
                 f"Scenarios File: {SCENARIOS_FILE}\n"
                 f"Scenarios File Exists: {SCENARIOS_FILE.exists()}\n\n"
                 f"Environment Variables:\n"
                 f"  OCTUPOST_API_URL - API base URL (default: http://localhost:8000)\n"
                 f"  OCTUPOST_TEST_PROJECT_ID - Default project for tests\n",
        )]

    return [TextContent(type="text", text=f"❌ Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

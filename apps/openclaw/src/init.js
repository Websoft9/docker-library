#!/usr/bin/env node
/**
 * OpenClaw startup initializer for Docker / Websoft9.
 *
 * Runs BEFORE the gateway starts. Auto-configures AI providers based on
 * environment variables — no CLI commands needed for users.
 *
 * Writes to THREE locations (all layers of OpenClaw's auth stack):
 *   1. openclaw.json          — gateway-level provider/model config
 *   2. agents/main/agent/models.json       — agent model catalog
 *   3. agents/main/agent/auth-profiles.json — agent API key store
 *
 * Supported env vars (set in .env):
 *   国内主流大模型 (Domestic AI providers):
 *   DEEPSEEK_API_KEY       → deepseek/deepseek-chat   (custom provider)
 *   BAIDU_API_KEY/SECRET   → baidu/ernie-*             (百度文心一言)
 *   ALIBABA_API_KEY        → alibaba/qwen-*            (阿里通义千问)
 *   MOONSHOT_API_KEY       → moonshot/moonshot-v1-*    (月之暗面 Kimi)
 *
 *   WeCom channel (@sunnoy/wecom — community-enhanced plugin):
 *   WebSocket persistent connection, no callback URL needed.
 *   WECOM_BOT_ID           → Bot ID (机器人ID) from WeCom AI Bot console
 *   WECOM_BOT_SECRET       → Bot Secret (机器人密钥) from WeCom AI Bot console
 *   WECOM_DM_POLICY        → Private chat policy: open|pairing|allowlist|disabled (default: open)
 *   Optional Agent (enhanced outbound — file/image/dept/tag sending):
 *   WECOM_AGENT_CORP_ID    → corpId of self-built app (wwXXXXXX)
 *   WECOM_AGENT_SECRET     → corpSecret of self-built app
 *   WECOM_AGENT_ID         → agentId of self-built app (number)
 */

'use strict';

const fs = require('fs');
const path = require('path');

const OPENCLAW_DIR = '/home/node/.openclaw';
const CONFIG_PATH = path.join(OPENCLAW_DIR, 'openclaw.json');
const AGENT_DIR = path.join(OPENCLAW_DIR, 'agents/main/agent');
const AGENT_MODELS = path.join(AGENT_DIR, 'models.json');
const AUTH_PROFILES = path.join(AGENT_DIR, 'auth-profiles.json');

fs.mkdirSync(OPENCLAW_DIR, { recursive: true });
fs.mkdirSync(AGENT_DIR, { recursive: true });

// ── Environment variable mapping (W9_*_SET UI-configurable vars) ─────────────
// This allows Websoft9 app store to expose these as form fields while
// maintaining backward compatibility with non-W9 variable names.
const env = {
    // AI Models — W9_*_SET takes precedence, fallback to original name
    DEEPSEEK_API_KEY: process.env.W9_DEEPSEEK_API_KEY_SET || process.env.DEEPSEEK_API_KEY,
    BAIDU_API_KEY: process.env.W9_BAIDU_API_KEY_SET,
    BAIDU_SECRET_KEY: process.env.W9_BAIDU_SECRET_KEY_SET,
    ALIBABA_API_KEY: process.env.W9_ALIBABA_API_KEY_SET,
    MOONSHOT_API_KEY: process.env.W9_MOONSHOT_API_KEY_SET,

    // WeCom (企业微信) — @sunnoy/wecom plugin
    WECOM_BOT_ID: process.env.W9_WECOM_BOT_ID_SET || process.env.WECOM_BOT_ID,
    WECOM_BOT_SECRET: process.env.W9_WECOM_BOT_SECRET_SET || process.env.WECOM_BOT_SECRET,
    WECOM_DM_POLICY: process.env.W9_WECOM_DM_POLICY_SET || process.env.WECOM_DM_POLICY || 'open',
    // Optional: Self-built App for enhanced outbound (file/image/dept/tag)
    WECOM_AGENT_CORP_ID: process.env.W9_WECOM_AGENT_CORP_ID_SET || process.env.WECOM_AGENT_CORP_ID,
    WECOM_AGENT_SECRET: process.env.W9_WECOM_AGENT_SECRET_SET || process.env.WECOM_AGENT_SECRET,
    WECOM_AGENT_ID: process.env.W9_WECOM_AGENT_ID_SET || process.env.WECOM_AGENT_ID,

};

// ── Load existing openclaw.json ───────────────────────────────────────────────
let config = {};
try {
    config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
    console.log('[init] Loaded existing openclaw.json');
} catch (_) {
    console.log('[init] Starting fresh openclaw.json');
}

// ── Gateway (always overwrite from env) ───────────────────────────────────────
config.gateway = {
    mode: 'local',
    bind: process.env.OPENCLAW_GATEWAY_BIND || 'lan',
    auth: { mode: 'token', token: process.env.OPENCLAW_GATEWAY_TOKEN },
    controlUi: {
        allowedOrigins: ['*'],
        // Disable per-device pairing for Docker deployments — the gateway token
        // already provides sufficient access control. Without this, every new
        // browser requires manual `openclaw devices approve` which is impractical.
        dangerouslyDisableDeviceAuth: true
    }
};

// Only allow @sunnoy/wecom plugin (plugin id = "wecom", directory = "wecom")
config.plugins = { allow: ['wecom'] };

// ── Build provider + auth lists ───────────────────────────────────────────────
const gatewayProviders = (config.models && config.models.providers) || {};
const agentModels = { providers: {} };
const authProfiles = { version: 1, profiles: {} };

// ── DeepSeek (custom — needs config in all three files) ───────────────────────
if (env.DEEPSEEK_API_KEY) {
    const deepseekDef = {
        baseUrl: 'https://api.deepseek.com/v1',
        apiKey: env.DEEPSEEK_API_KEY,
        api: 'openai-completions',
        authHeader: true,
        models: [
            {
                id: 'deepseek-chat', name: 'DeepSeek V3 (deepseek-chat)',
                api: 'openai-completions', reasoning: false, input: ['text'],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 65536, maxTokens: 8192
            },
            {
                id: 'deepseek-reasoner', name: 'DeepSeek R1 (deepseek-reasoner)',
                api: 'openai-completions', reasoning: true, input: ['text'],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 65536, maxTokens: 8192
            }
        ]
    };
    gatewayProviders.deepseek = deepseekDef;
    agentModels.providers.deepseek = deepseekDef;
    authProfiles.profiles['deepseek:default'] = {
        type: 'api_key', mode: 'api_key',
        provider: 'deepseek',
        apiKey: env.DEEPSEEK_API_KEY
    };
    console.log('[init] DeepSeek configured (gateway + models + auth-profiles)');
} else {
    delete gatewayProviders.deepseek;
}

// ── Baidu ERNIE (百度文心) ────────────────────────────────────────────────────
// Baidu Qianfan uses OAuth2: must exchange API Key + Secret Key for access_token
// API doc: https://cloud.baidu.com/doc/WENXINWORKSHOP/s/flfmc9do2
if (env.BAIDU_API_KEY && env.BAIDU_SECRET_KEY) {
    const baiduDef = {
        baseUrl: 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat',
        apiKey: env.BAIDU_API_KEY,       // For OAuth token fetch
        secretKey: env.BAIDU_SECRET_KEY, // For OAuth token fetch
        api: 'baidu-chat',  // Custom API adapter (OpenClaw will need to implement this)
        authHeader: false,  // Auth via ?access_token= query param
        models: [
            {
                id: 'ernie-4.0-turbo-8k', name: 'ERNIE 4.0 Turbo',
                api: 'baidu-chat', reasoning: false, input: ['text'],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 8192, maxTokens: 2048
            },
            {
                id: 'ernie-3.5-8k', name: 'ERNIE 3.5',
                api: 'baidu-chat', reasoning: false, input: ['text'],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 8192, maxTokens: 2048
            },
            {
                id: 'ernie-speed-128k', name: 'ERNIE Speed 128K',
                api: 'baidu-chat', reasoning: false, input: ['text'],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 131072, maxTokens: 4096
            }
        ]
    };
    gatewayProviders.baidu = baiduDef;
    agentModels.providers.baidu = baiduDef;
    authProfiles.profiles['baidu:default'] = {
        type: 'api_key', mode: 'api_key',
        provider: 'baidu',
        apiKey: env.BAIDU_API_KEY,
        secretKey: env.BAIDU_SECRET_KEY  // Non-standard: Baidu needs both keys
    };
    console.log('[init] Baidu ERNIE configured (requires baidu-chat API adapter)');
} else {
    delete gatewayProviders.baidu;
}

// ── Alibaba Qwen (阿里通义千问) ───────────────────────────────────────────────
// DashScope API: https://help.aliyun.com/zh/dashscope/developer-reference/api-details
if (env.ALIBABA_API_KEY) {
    const aliDef = {
        baseUrl: 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
        apiKey: env.ALIBABA_API_KEY,
        api: 'qwen-chat',  // Custom API adapter
        authHeader: true,  // Authorization: Bearer <API-KEY>
        models: [
            {
                id: 'qwen-max', name: 'Qwen Max (最强推理)',
                api: 'qwen-chat', reasoning: false, input: ['text'],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 30720, maxTokens: 8192
            },
            {
                id: 'qwen-plus', name: 'Qwen Plus (平衡性价比)',
                api: 'qwen-chat', reasoning: false, input: ['text'],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 131072, maxTokens: 8192
            },
            {
                id: 'qwen-turbo', name: 'Qwen Turbo (极速响应)',
                api: 'qwen-chat', reasoning: false, input: ['text'],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 131072, maxTokens: 8192
            }
        ]
    };
    gatewayProviders.alibaba = aliDef;
    agentModels.providers.alibaba = aliDef;
    authProfiles.profiles['alibaba:default'] = {
        type: 'api_key', mode: 'api_key',
        provider: 'alibaba',
        apiKey: env.ALIBABA_API_KEY
    };
    console.log('[init] Alibaba Qwen configured (requires qwen-chat API adapter)');
} else {
    delete gatewayProviders.alibaba;
}

// ── Moonshot (月之暗面 Kimi) ──────────────────────────────────────────────────
// OpenAI-compatible API: https://platform.moonshot.cn/docs/api-reference
if (env.MOONSHOT_API_KEY) {
    const moonshotDef = {
        baseUrl: 'https://api.moonshot.cn/v1',
        apiKey: env.MOONSHOT_API_KEY,
        api: 'openai-completions',  // OpenAI-compatible
        authHeader: true,
        models: [
            {
                id: 'moonshot-v1-8k', name: 'Moonshot v1 8K',
                api: 'openai-completions', reasoning: false, input: ['text'],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 8192, maxTokens: 4096
            },
            {
                id: 'moonshot-v1-32k', name: 'Moonshot v1 32K',
                api: 'openai-completions', reasoning: false, input: ['text'],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 32768, maxTokens: 4096
            },
            {
                id: 'moonshot-v1-128k', name: 'Moonshot v1 128K',
                api: 'openai-completions', reasoning: false, input: ['text'],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 131072, maxTokens: 4096
            }
        ]
    };
    gatewayProviders.moonshot = moonshotDef;
    agentModels.providers.moonshot = moonshotDef;
    authProfiles.profiles['moonshot:default'] = {
        type: 'api_key', mode: 'api_key',
        provider: 'moonshot',
        apiKey: env.MOONSHOT_API_KEY
    };
    console.log('[init] Moonshot configured (OpenAI-compatible)');
} else {
    delete gatewayProviders.moonshot;
}

// ── WeCom Channel (@sunnoy/wecom) ────────────────────────────────────────────
// WebSocket persistent connection — no callback URL needed.
// Plugin is guaranteed by Dockerfile, no filesystem check required.
// Optional Agent config enables file/image/dept/tag outbound sending.
const hasWeCom = !!(env.WECOM_BOT_ID && env.WECOM_BOT_SECRET);
const hasWeComAgent = !!(env.WECOM_AGENT_CORP_ID && env.WECOM_AGENT_SECRET && env.WECOM_AGENT_ID);

if (hasWeCom) {
    const wecomConfig = {
        enabled: true,
        botId: env.WECOM_BOT_ID,
        secret: env.WECOM_BOT_SECRET,
        // dmPolicy: open = all members can chat directly (no pairing approval needed)
        // options: open | pairing | allowlist | disabled
        dmPolicy: env.WECOM_DM_POLICY
    };

    // Optional: Self-built App for enhanced outbound (file/image/dept/tag sending)
    // Does NOT need token/encodingAESKey — Agent only handles outbound, not inbound.
    if (hasWeComAgent) {
        wecomConfig.agent = {
            corpId: env.WECOM_AGENT_CORP_ID,
            corpSecret: env.WECOM_AGENT_SECRET,
            agentId: parseInt(env.WECOM_AGENT_ID, 10)
        };
    }

    config.channels = config.channels || {};
    config.channels['wecom'] = wecomConfig;

    // Add/update binding to the main agent (preserving any other bindings)
    const wecomBinding = { agentId: 'main', match: { channel: 'wecom' } };
    const otherBindings = (Array.isArray(config.bindings) ? config.bindings : [])
        .filter(b => !(b.match && b.match.channel === 'wecom'));
    config.bindings = [...otherBindings, wecomBinding];

    const agentLabel = hasWeComAgent ? ' + Agent(outbound)' : '';
    console.log('[init] WeCom configured (WebSocket' + agentLabel + ', dmPolicy=' + env.WECOM_DM_POLICY + ', botId=' + env.WECOM_BOT_ID + ')');
} else {
    // Remove WeCom config when credentials not provided
    if (config.channels && config.channels['wecom']) {
        delete config.channels['wecom'];
        if (Object.keys(config.channels).length === 0) delete config.channels;
    }
    if (Array.isArray(config.bindings)) {
        config.bindings = config.bindings.filter(
            b => !(b.match && b.match.channel === 'wecom')
        );
        if (config.bindings.length === 0) delete config.bindings;
    }
    console.log('[init] WeCom skipped — set W9_WECOM_BOT_ID_SET and W9_WECOM_BOT_SECRET_SET to enable');
}

// ── Write models.json ─────────────────────────────────────────────────────────
if (Object.keys(agentModels.providers).length > 0) {
    fs.writeFileSync(AGENT_MODELS, JSON.stringify(agentModels, null, 2));
    console.log('[init] models.json written');
} else {
    try { fs.unlinkSync(AGENT_MODELS); } catch (_) { }
}

// ── Write auth-profiles.json ──────────────────────────────────────────────────
if (Object.keys(authProfiles.profiles).length > 0) {
    fs.writeFileSync(AUTH_PROFILES, JSON.stringify(authProfiles, null, 2));
    console.log('[init] auth-profiles.json written');
} else {
    try { fs.unlinkSync(AUTH_PROFILES); } catch (_) { }
}

// ── Write openclaw.json (gateway + model defaults) ────────────────────────────
if (Object.keys(gatewayProviders).length > 0) {
    config.models = { mode: 'merge', providers: gatewayProviders };
} else {
    delete config.models;
}

// Default model — always recalculate so stale refs are cleared if key removed
// Priority: DeepSeek → Moonshot → Baidu → Alibaba
let defaultModel = null;
if (env.DEEPSEEK_API_KEY) defaultModel = 'deepseek/deepseek-chat';
else if (env.MOONSHOT_API_KEY) defaultModel = 'moonshot/moonshot-v1-32k';
else if (env.BAIDU_API_KEY) defaultModel = 'baidu/ernie-4.0-turbo-8k';
else if (env.ALIBABA_API_KEY) defaultModel = 'alibaba/qwen-max';

if (defaultModel) {
    config.agents = config.agents || {};
    config.agents.defaults = config.agents.defaults || {};
    config.agents.defaults.model = { primary: defaultModel };
    config.agents.defaults.workspace = config.agents.defaults.workspace || '~/.openclaw/workspace';
    console.log('[init] Default model:', defaultModel);
} else {
    if (config.agents && config.agents.defaults) delete config.agents.defaults.model;
    console.log('[init] No API key — configure one in .env and restart');
}

fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
console.log('[init] openclaw.json written');

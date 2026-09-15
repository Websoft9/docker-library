<?php

$w9_url = getenv('W9_URL');

$w9_redis_host = getenv('WP_REDIS_HOST');
$w9_redis_port = getenv('WP_REDIS_PORT');
$w9_redis_database = getenv('WP_REDIS_DATABASE');
$w9_redis_prefix = getenv('WP_REDIS_PREFIX');
$w9_redis_client = getenv('WP_REDIS_CLIENT');
$w9_redis_timeout = getenv('WP_REDIS_TIMEOUT');
$w9_redis_read_timeout = getenv('WP_REDIS_READ_TIMEOUT');

if ($w9_url) {
    $w9_scheme = (
        isset($_SERVER['HTTP_X_FORWARDED_PROTO'])
        && stripos($_SERVER['HTTP_X_FORWARDED_PROTO'], 'https') !== false
    ) ? 'https' : 'http';

    if ($w9_scheme === 'https') {
        $_SERVER['HTTPS'] = 'on';
    }

    $w9_root = preg_match('#^https?://#i', $w9_url)
        ? $w9_url
        : $w9_scheme . '://' . $w9_url;

    if (!defined('WP_HOME')) {
        define('WP_HOME', $w9_root);
    }
    if (!defined('WP_SITEURL')) {
        define('WP_SITEURL', $w9_root);
    }
}

if ($w9_redis_host) {
    if (!defined('WP_CACHE')) {
        define('WP_CACHE', true);
    }
    if (!defined('WP_REDIS_HOST')) {
        define('WP_REDIS_HOST', $w9_redis_host);
    }
    if (!defined('WP_REDIS_PORT') && $w9_redis_port !== false && $w9_redis_port !== '') {
        define('WP_REDIS_PORT', (int) $w9_redis_port);
    }
    if (!defined('WP_REDIS_DATABASE') && $w9_redis_database !== false && $w9_redis_database !== '') {
        define('WP_REDIS_DATABASE', (int) $w9_redis_database);
    }
    if (!defined('WP_REDIS_PREFIX') && $w9_redis_prefix !== false && $w9_redis_prefix !== '') {
        define('WP_REDIS_PREFIX', $w9_redis_prefix);
    }
    if (!defined('WP_REDIS_CLIENT') && $w9_redis_client !== false && $w9_redis_client !== '') {
        define('WP_REDIS_CLIENT', $w9_redis_client);
    }
    if (!defined('WP_REDIS_TIMEOUT') && $w9_redis_timeout !== false && $w9_redis_timeout !== '') {
        define('WP_REDIS_TIMEOUT', (int) $w9_redis_timeout);
    }
    if (!defined('WP_REDIS_READ_TIMEOUT') && $w9_redis_read_timeout !== false && $w9_redis_read_timeout !== '') {
        define('WP_REDIS_READ_TIMEOUT', (int) $w9_redis_read_timeout);
    }
}

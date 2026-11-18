<?php

$wp_forwarded_https = (
    isset($_SERVER['HTTP_X_FORWARDED_PROTO'])
    && stripos($_SERVER['HTTP_X_FORWARDED_PROTO'], 'https') !== false
);

$w9_redis_host = getenv('WP_REDIS_HOST');
$w9_redis_port = getenv('WP_REDIS_PORT');
$w9_redis_database = getenv('WP_REDIS_DATABASE');
$w9_redis_prefix = getenv('WP_REDIS_PREFIX');
$w9_redis_client = getenv('WP_REDIS_CLIENT');
$w9_redis_timeout = getenv('WP_REDIS_TIMEOUT');
$w9_redis_read_timeout = getenv('WP_REDIS_READ_TIMEOUT');

if ($wp_forwarded_https) {
    $_SERVER['HTTPS'] = 'on';
}

$wp_scheme = $wp_forwarded_https ? 'https' : 'http';
$wp_home = trim((string) getenv('WP_HOME'));
$wp_siteurl = trim((string) (getenv('WP_SITEURL') ?: $wp_home));

if ($wp_home !== '' && !defined('WP_HOME')) {
    $wp_home_url = preg_match('#^https?://#i', $wp_home)
        ? rtrim($wp_home, '/')
        : $wp_scheme . '://' . rtrim($wp_home, '/');
    define('WP_HOME', $wp_home_url);
}

if ($wp_siteurl !== '' && !defined('WP_SITEURL')) {
    $wp_site_url = preg_match('#^https?://#i', $wp_siteurl)
        ? rtrim($wp_siteurl, '/')
        : $wp_scheme . '://' . rtrim($wp_siteurl, '/');
    define('WP_SITEURL', $wp_site_url);
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

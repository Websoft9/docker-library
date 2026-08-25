<?php

$w9_url = getenv('W9_URL');

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
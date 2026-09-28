'use strict';

module.exports = {
  register() {},

  async bootstrap({ strapi }) {
    const email = process.env.W9_LOGIN_USER;
    const password = process.env.W9_LOGIN_PASSWORD;

    if (!email || !password) {
      return;
    }

    const userService = strapi.admin?.services?.user;
    if (!userService) {
      return;
    }

    const adminCount = await userService.count();
    if (adminCount > 0) {
      return;
    }

    await userService.createFirstAdmin({
      email,
      password,
      firstname: 'Strapi',
      lastname: 'Admin',
    });

    strapi.log.info(`Created initial Strapi administrator: ${email}`);
  },
};

module.exports = ({ config }) => {
  return {
    ...config,
    experiments: {
      ...(config.experiments || {}),
      baseUrl: process.env.BASE_URL || "",
    },
  };
};

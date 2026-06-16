import js from "@eslint/js";
import pluginVue from "eslint-plugin-vue";

export default [
  js.configs.recommended,
  ...pluginVue.configs["flat/recommended"],
  {
    files: ["**/*.{js,vue}"],
    rules: {
      "vue/multi-word-component-names": "off",
    },
  },
  {
    ignores: ["dist", "node_modules"],
  },
];

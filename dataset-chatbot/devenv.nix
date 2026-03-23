{
  pkgs,
  lib,
  config,
  inputs,
  ...
}:

{
  languages = {
    python = {
      enable = true;
      package = pkgs.python314;
      uv.enable = true;
    };
  };

  env.OPENAI_API_KEY = config.secretspec.secrets.OPENAI_API_KEY;
}

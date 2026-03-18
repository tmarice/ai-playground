{
  pkgs,
  lib,
  config,
  inputs,
  ...
}:

{
  packages = with pkgs; [
    just
  ];

  languages = {
    python = {
      enable = true;
      package = pkgs.python314;
      uv.enable = true;
    };

    javascript = {
      enable = true;
      package = pkgs.nodejs_22;
      pnpm.enable = true;
    };
  };
}

{ hostName
, extraModules ? [ ]
, extraConfig ? { }
}:
{ config, pkgs, lib, ... }:
let
  repoRoot = ../../.;
  defaultSecretsPath = "${toString repoRoot}/secrets/secret_default.nix";

  outsideRepoSecretsPath = "${toString repoRoot}/../nixos/secrets/secret.nix";

  envSecretPath =
    let
      raw = builtins.getEnv "TONY_SECRETS_PATH";
      pwd = builtins.getEnv "PWD";
    in
      if raw == "" then null
      else if lib.hasPrefix "/" raw then raw
      else if pwd != "" then "${pwd}/${raw}"
      else raw;

  secretsPathCandidates =
    (lib.optional (envSecretPath != null) envSecretPath)
    ++ [ "/etc/nixos-config/secrets/secret.nix"
         outsideRepoSecretsPath
         "${toString repoRoot}/secrets/secret.nix"
       ];

  secretsSource =
    let
      found = lib.filter builtins.pathExists secretsPathCandidates;
    in
      if found != [ ] then builtins.head found
      else if builtins.pathExists defaultSecretsPath then defaultSecretsPath
      else throw ''No secrets file found. Provide one of:
- export TONY_SECRETS_PATH=<path> pointing to your secrets file (requires --impure when using flakes)
- ${toString repoRoot}/secrets/secret.nix (gitignored local copy)
- /etc/nixos-config/secrets/secret.nix
Or create ${defaultSecretsPath} from the template.'';
  secrets = import secretsSource;

  hostSecrets =
    if builtins.hasAttr hostName secrets
    then builtins.getAttr hostName secrets
    else throw "Missing secrets for ${hostName} in \"${secretsSource}\".";

  primaryUser =
    if builtins.hasAttr "primaryUser" hostSecrets
    then hostSecrets.primaryUser
    else throw "Missing primaryUser entry for ${hostName}.";

  primaryUserName =
    if builtins.hasAttr "name" primaryUser
    then primaryUser.name
    else throw "Missing primaryUser.name for ${hostName}.";

  primaryUserPasswordHash =
    if builtins.hasAttr "passwordHash" primaryUser
    then primaryUser.passwordHash
    else throw "Missing primaryUser.passwordHash for ${hostName}.";

  primaryUserDescription =
    if builtins.hasAttr "description" primaryUser
    then primaryUser.description
    else primaryUserName;

  primaryUserExtraGroups =
    if builtins.hasAttr "extraGroups" primaryUser
    then primaryUser.extraGroups
    else [ "wheel" "networkmanager" ];

  primaryUserAuthorizedKeys =
    if builtins.hasAttr "authorizedKeys" primaryUser
    then primaryUser.authorizedKeys
    else [ ];

  rootPasswordHash =
    if builtins.hasAttr "rootPasswordHash" hostSecrets
    then hostSecrets.rootPasswordHash
    else throw "Missing rootPasswordHash for ${hostName}.";

  stateVersion =
    if builtins.hasAttr "stateVersion" hostSecrets
    then hostSecrets.stateVersion
    else "23.11";

  hardwarePath = ../${hostName}/hardware-configuration.nix;

  hardwareModules =
    if builtins.pathExists hardwarePath
    then [ hardwarePath ]
    else lib.warn "Hardware configuration for ${hostName} was not found at ${hardwarePath}." [ ];

in
{
  imports = hardwareModules ++ [ ../common/base.nix ] ++ extraModules;

  networking.hostName = hostName;

  users.mutableUsers = false;
  users.users = {
    root = {
      hashedPassword = rootPasswordHash;
    };
    "${primaryUserName}" = {
      isNormalUser = true;
      description = primaryUserDescription;
      hashedPassword = primaryUserPasswordHash;
      extraGroups = primaryUserExtraGroups;
      openssh.authorizedKeys.keys = primaryUserAuthorizedKeys;
    };
  };

  system.stateVersion = lib.mkDefault stateVersion;
}
// extraConfig

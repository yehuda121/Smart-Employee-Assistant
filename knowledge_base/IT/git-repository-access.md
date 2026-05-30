# Git Repository Access (GitLab Enterprise)

## Purpose

This article defines the procedure for requesting and managing access to Amdocs GitLab Enterprise repositories at `gitlab.amdocs.internal`. GitLab is the sole approved source code management platform for Amdocs software development and related DevOps workflows.

## Scope

This procedure applies to all Amdocs engineers, QA staff, DevOps personnel, and approved contractors who require access to GitLab projects, groups, or snippets. It covers the self-hosted GitLab instance and does not apply to personal GitHub or Bitbucket accounts used for non-Amdocs work.

## Procedure

1. **Verify baseline access.** All employees in engineering job families (Job Family Code: ENG-*) receive GitLab **Developer** role at the group level upon hire. Confirm your access by navigating to `https://gitlab.amdocs.internal` and logging in with Amdocs SSO (Okta).

2. **Request project-specific access.** For projects outside your default group, submit a ServiceNow request under **Access Management > GitLab Repository Access**. Include the GitLab project path (e.g., `billing/ces-integration`), desired role (Guest, Reporter, Developer, Maintainer, Owner), and Jira epic or project reference.

3. **Obtain maintainer approval.** The project's designated Maintainer (listed in GitLab under **Project Information > Members**) approves the request. Owner-level access requires director approval and Information Security review.

4. **Configure SSH keys.** Generate an SSH key pair on your Amdocs device (`ssh-keygen -t ed25519 -C "firstname.lastname@amdocs.com"`). Add the public key in GitLab under **User Settings > SSH Keys**. Do not use RSA keys shorter than 4096 bits.

5. **Clone repositories.** Use SSH URLs exclusively for development work: `git clone git@gitlab.amdocs.internal:billing/ces-integration.git`. HTTPS clone is permitted for read-only CI/CD pipelines only.

6. **Follow branch protection rules.** All production-bound repositories enforce branch protection on `main` and `release/*` branches: minimum one approval, pipeline must pass, no force push. Direct commits to protected branches are blocked.

7. **Request access revocation.** When leaving a project or the company, access is revoked through offboarding automation (KB-HR-005). For mid-project removal, the project Maintainer removes the user from the project members list and notifies the Security team if the user had Maintainer or Owner role.

## Important Notes

- VPN connection is required for GitLab access from outside Amdocs offices (except Ra'anana HQ direct route).
- Two-factor authentication on GitLab is enforced via Okta SSO; standalone GitLab passwords are disabled.
- Commit signing with GPG is mandatory for all commits to `main` and `release/*` branches. Setup guide: KB-IT-0098.
- Do not store secrets, API keys, or credentials in repositories. Use GitLab CI/CD variables or HashiCorp Vault (`vault.amdocs.internal`).
- External collaborators receive Guest or Reporter roles only and must use Amdocs-provisioned accounts (no external GitLab.com federation).
- Repository size limit is 10 GB. Large binary files must use Git LFS, configured per project.

## Contact Information

- **DevOps Platform Team:** devops-platform@amdocs.com
- **GitLab Admin:** gitlab-admin@amdocs.com
- **IT Service Desk:** servicedesk@amdocs.com | Internal ext. 4357

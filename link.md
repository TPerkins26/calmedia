https://thomasperkins.github.io/calmedia/social.html#friends

## CalMedia GitHub Pages Deployment
- **Live Social & Networking Hub**: https://thomasperkins.github.io/calmedia/social.html#friends
- **Full Application**: https://thomasperkins.github.io/calmedia/index.html
- **Monorepo Subpath Link**: https://drchangliu.github.io/htc/TP_Project_2.1/site/social.html#friends

### GitHub Pages Setup Instructions
1. In your GitHub repository settings, navigate to **Settings** → **Pages**.
2. Under **Build and deployment**:
   - Source: **Deploy from a branch**
   - Branch: `main` / Folder: `/ (root)` (if repository root contains the site) or specify the GitHub Actions static deployment workflow.
3. The application is 100% client-side compatible:
   - Contains a built-in LocalStorage data engine with 5 seeded campus profiles (Alice, Bob, Charlie, Dana, Evan).
   - Fully supports **Account Creation** (name, `@handle`, emoji avatar, bio, Discord tag, calendar feed link, privacy mode).
   - Fully supports **Campus Networking & Friends** (send friend requests, incoming request alerts, accept/decline, unfriend, and 1-click schedule comparisons).
   - Implements mathematical set intersection for mutual free times ($08:00 - 22:00$) entirely in client-side JavaScript.
   - Interactive Discord bot simulation console for `/today`, `/free`, `/meet`, and moment photo sharing.

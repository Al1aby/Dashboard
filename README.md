# Nauwigewauk Community Club — Website

A full multi-page website for the Nauwigewauk Community Club, ready for deployment on GitHub Pages.

---

## Files in This Package

| File | Description |
|------|-------------|
| `index.html` | Homepage |
| `news-events.html` | News & Events page |
| `executive.html` | Executive & volunteers page |
| `facilities.html` | Facilities & hall rental page |
| `nature-trail.html` | Nature Trail page |
| `photo-archive.html` | Photo Archive page |
| `contact.html` | Contact page |
| `style.css` | Shared stylesheet (used by all pages) |
| `nav.js` | Shared navigation & footer (used by all pages) |
| `NBCC_logo.png` | Club logo — **place this file in the same folder** |

---

## How to Deploy on GitHub Pages (Free Hosting)

### Step 1 — Create a GitHub Account
Go to [github.com](https://github.com) and sign up for a free account if you don't have one.

### Step 2 — Create a New Repository
1. Click the **+** button → **New repository**
2. Name it: `nauwigewauk` (or any name you like)
3. Set it to **Public**
4. Click **Create repository**

### Step 3 — Upload Your Files
1. On your new repository page, click **uploading an existing file**
2. Drag and drop ALL files from this folder (including `NBCC_logo.png`)
3. Click **Commit changes**

### Step 4 — Enable GitHub Pages
1. Go to your repository → **Settings** tab
2. In the left sidebar click **Pages**
3. Under "Source", select **Deploy from a branch**
4. Set Branch to **main**, folder to **/ (root)**
5. Click **Save**

### Step 5 — Your Site is Live!
After 1–2 minutes, your site will be live at:
`https://[your-github-username].github.io/nauwigewauk/`

---

## Connecting Your GoDaddy Domain

Once your site is live on GitHub Pages:

1. In GoDaddy, go to **My Domains** → **DNS** for your domain
2. Add a **CNAME record**:
   - Name: `www`
   - Value: `[your-github-username].github.io`
3. In GitHub → Settings → Pages, under **Custom domain**, enter your domain (e.g. `www.nauwigewauk.ca`)
4. Check **Enforce HTTPS**

DNS changes can take up to 24 hours to propagate.

---

## Making the Contact Form Work

The contact form on `contact.html` needs a backend to send emails. The easiest free option is **Formspree**:

1. Go to [formspree.io](https://formspree.io) and create a free account
2. Create a new form and get your endpoint URL (looks like `https://formspree.io/f/xxxxxxxx`)
3. In `contact.html`, find this line:
   ```html
   <form class="contact-form" action="#" method="POST">
   ```
4. Replace `action="#"` with your Formspree URL:
   ```html
   <form class="contact-form" action="https://formspree.io/f/xxxxxxxx" method="POST">
   ```

---

## Updating Content

All placeholder text is marked with notices like:
> 📋 **For the Club Executive** — Replace the sample content below with your actual information.

### To add photos to the archive:
1. Place your image files in the site folder
2. Open `photo-archive.html`
3. Find the `photo-placeholder` divs and replace them with:
   ```html
   <div class="photo-card">
     <img src="your-photo-filename.jpg" alt="Description of photo" />
     <div class="photo-overlay">
       <p class="photo-caption">Your caption here, circa 1965</p>
     </div>
   </div>
   ```

### To embed a Google Map on the Contact page:
1. Go to [maps.google.com](https://maps.google.com)
2. Search for the club location
3. Click **Share** → **Embed a map** → Copy the HTML
4. Paste it in `contact.html` where the map placeholder is

---

## Need Help?

Contact the person who built this site or reach out to GitHub support at [docs.github.com](https://docs.github.com).

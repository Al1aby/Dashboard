/* calendar-widget.js
   Fetches the next N upcoming events from a public Google Calendar
   and renders them in NCC's own styling (no Google branding/iframe).

   SETUP: replace API_KEY below with your restricted Google Cloud API key.
*/
(function () {
  const CALENDAR_ID = 'nauwigewaukcommunityclub@gmail.com';
  const API_KEY = 'AIzaSyCRerBU7HQ_1-NABw9LKUfhiVbGeRlds94'; // Google Cloud API key, restricted to Calendar API + this site's domains
  const DEFAULT_MAX_EVENTS = 5;
  const TIMEZONE = 'America/Moncton';

  const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str == null ? '' : str;
    return div.innerHTML;
  }

  function renderEvents(container, events, variant) {
    if (!events.length) {
      container.innerHTML = '<div class="gcal-empty">No upcoming events right now — check back soon.</div>';
      return;
    }
    if (variant === 'feature') {
      container.innerHTML = events.map(ev => {
        const startStr = ev.start.dateTime || ev.start.date;
        const dt = new Date(startStr);
        const month = MONTHS[dt.getMonth()];
        const day = dt.getDate();
        let timeStr = 'All day';
        if (ev.start.dateTime) {
          timeStr = dt.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', timeZone: TIMEZONE });
        }
        const location = ev.location ? ` · ${escapeHtml(ev.location)}` : '';
        const title = escapeHtml(ev.summary || 'Untitled Event');
        return `
          <div class="event-date-row">
            <div class="edr-badge"><span class="m">${month}</span><span class="d">${day}</span></div>
            <div><div class="edr-time">${timeStr}${location}</div><div class="edr-title">${title}</div></div>
          </div>`;
      }).join('');
      return;
    }
    container.innerHTML = events.map(ev => {
      const startStr = ev.start.dateTime || ev.start.date;
      const dt = new Date(startStr);
      const month = MONTHS[dt.getMonth()];
      const day = dt.getDate();
      let timeStr = 'All day';
      if (ev.start.dateTime) {
        timeStr = dt.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', timeZone: TIMEZONE });
      }
      const location = ev.location ? ` · ${escapeHtml(ev.location)}` : '';
      const title = escapeHtml(ev.summary || 'Untitled Event');
      return `
        <div class="gcal-event">
          <div class="gcal-date"><span class="gcal-month">${month}</span><span class="gcal-day">${day}</span></div>
          <div class="gcal-info">
            <div class="gcal-title">${title}</div>
            <div class="gcal-meta">${timeStr}${location}</div>
          </div>
        </div>`;
    }).join('');
  }

  async function loadCalendarWidget(containerId, maxEvents, variant) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const limit = maxEvents || DEFAULT_MAX_EVENTS;

    if (!API_KEY || API_KEY === 'YOUR_API_KEY_HERE') {
      container.innerHTML = '<div class="gcal-empty">Calendar widget not yet configured — add a Google Calendar API key in calendar-widget.js.</div>';
      return;
    }

    const timeMin = encodeURIComponent(new Date().toISOString());
    const url = `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(CALENDAR_ID)}/events` +
      `?key=${API_KEY}&timeMin=${timeMin}&maxResults=${limit}&orderBy=startTime&singleEvents=true`;

    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error('Calendar request failed: ' + res.status);
      const data = await res.json();
      renderEvents(container, data.items || [], variant);
    } catch (err) {
      console.error('Calendar widget error:', err);
      container.innerHTML = `<div class="gcal-error">Couldn't load events right now. <a href="https://calendar.google.com/calendar/embed?src=nauwigewaukcommunityclub%40gmail.com" target="_blank" rel="noopener">View the calendar directly →</a></div>`;
    }
  }

  // Expose globally so any page can call it
  window.loadCalendarWidget = loadCalendarWidget;
})();

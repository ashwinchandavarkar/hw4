# Campus Customs — design summary

The goal was to make the site feel like a real, premium Campus Customs storefront
— confident, collegiate, and clearly Yale — rather than a generic template, while
staying within the black-and-gold brand. Here is what changed and why it should
keep shoppers browsing and buying.

## Fonts
- Added a deliberate type pairing: **Oswald** (a condensed, uppercase, athletic
  display face) for the wordmark, nav, headings, buttons, prices, and product
  names, with **Archivo** for body text. The condensed caps read as *collegiate
  varsity*, instantly signalling licensed Yale spirit wear.
- *Why it sells:* a distinctive, on-brand voice builds trust that this is the
  real shop, and prices/CTAs set in the display face read as decisive.

## Colors
- Deepened the palette into layered blacks with two soft gold radial glows behind
  the page, a reusable **gold gradient** (`--gold-grad`) used on the wordmark,
  buttons, badges, and accents, and gold selection + scrollbar details.
- *Why it sells:* the richer, consistent gold-on-black reads as premium and
  cohesive, so the merchandise feels worth its price.

## Visual hierarchy
- A larger hero headline (68px display caps with a gradient "Big Yale"), a pill
  "eyebrow," and clear section headings. Product cards lead with the image, then
  a display-face name, then a gold price and stock — the eye lands on what
  matters for a purchase.
- *Why it sells:* shoppers grasp the offer and price in a glance and move toward
  products faster.

## Motion and interactions
- Tasteful, purposeful motion: hero and product cards rise/fade in, buttons have
  a gold gradient with a light **shine sweep** on hover, nav links get an
  animated gold underline, and cards lift with a shadow while the product image
  **zooms** and a gold "View details →" bar slides up.
- All motion is disabled under `prefers-reduced-motion` for accessibility.
- *Why it sells:* subtle feedback makes the site feel alive and responsive,
  rewarding exploration and nudging clicks into product pages.

## Product presentation
- White-background product shots in rounded cards with hover zoom and a clear
  in-stock/out-of-stock signal; the detail page pairs a large image with a
  display-face title, bold gold price, color list, and a per-size availability
  table plus the size-aware **Add to Bag**.
- *Why it sells:* confident, consistent presentation and at-a-glance size/stock
  info reduce hesitation and make adding to the bag easy.

## Chat experience
- The assistant is personified as **"Dan, your shop guide"** with a Handsome-Dan
  bulldog avatar. The launcher gently **pulses** to invite use; opening the panel
  **pops** in; messages fade in; a real **animated typing indicator** replaces a
  static "loading"; and first-time users get **quick-reply chips** ("Show me
  hoodies", "Gift for a Yale dad", "Something under $40"). Matched products
  appear as clickable cards right in the conversation.
- *Why it sells:* a friendly, branded, low-effort way to get help (with products
  surfaced inline) keeps shoppers engaged and routes them straight to items they
  can buy.

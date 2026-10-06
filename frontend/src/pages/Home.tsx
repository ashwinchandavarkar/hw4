import { Link } from "react-router-dom";

export function Home() {
  return (
    <div className="page home">
      <section className="hero">
        <div className="hero-inner">
          <p className="eyebrow">Officially licensed Yale apparel</p>
          <h1>
            Big Pride, <span className="hl">Big Yale.</span>
          </h1>
          <p className="lede">
            Campus Customs has dressed the Yale community from our Broadway shop
            since 1973. From game-day tees to residential-college crewnecks, every
            piece is made for the long walk across Old Campus and every reunion
            after. Casual comfort, classic Bulldog pride.
          </p>
          <div className="hero-cta">
            <Link className="btn" to="/products">
              Shop the catalogue
            </Link>
            <Link className="btn ghost" to="/about">
              Our story
            </Link>
          </div>
        </div>
      </section>

      <section className="tiles">
        <div className="tile">
          <h3>Your college, your colors</h3>
          <p>
            Benjamin Franklin to Timothy Dwight — rep your residential college
            with crewnecks and hoodies built for New Haven winters.
          </p>
        </div>
        <div className="tile">
          <h3>Game-day &amp; The Game</h3>
          <p>
            Cheer on the Bulldogs across 25+ varsity sports, and gear up for the
            rivalry when Harvard comes to town.
          </p>
        </div>
        <div className="tile">
          <h3>Gifts for every Yalie</h3>
          <p>
            Yale Dad, Mom, Grandma, Uncle — thoughtful pieces for the whole family
            that cheers from the stands.
          </p>
        </div>
      </section>

      <section className="home-chat-hint">
        <h2>Not sure where to start?</h2>
        <p>
          Tap the chat in the bottom-right corner and tell our assistant what you
          need. It knows our live catalogue — real prices, real sizes — and will
          pull matching gear right onto your screen.
        </p>
      </section>
    </div>
  );
}

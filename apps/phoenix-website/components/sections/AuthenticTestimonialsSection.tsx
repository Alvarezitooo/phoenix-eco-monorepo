import React from 'react';
import { RenderHtml } from '../../components/RenderHtml';

const AuthenticTestimonialsSection: React.FC<{ customHtml?: string }> = ({ customHtml }) => {
  return (
    <section className="real-testimonials py-16 px-4 bg-gray-50">
      <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 text-gray-800">
        💬 Les Premiers Retours (Beta Testeurs)
      </h2>
      <div className="text-center max-w-2xl mx-auto mb-12">
        <p className="text-lg text-gray-600">
          Phoenix est encore jeune ! Nous n'avons pas encore de témoignages d'utilisateurs. Soyez
          les premiers à partager votre expérience et à façonner l'avenir de Phoenix.
        </p>
      </div>

      <div className="call-for-testimonials text-center mt-12 p-8 bg-purple-100 rounded-lg max-w-2xl mx-auto shadow-inner">
        <p className="text-xl font-semibold text-purple-800 mb-4">
          🤝 Vous aussi, aidez Phoenix à grandir !
        </p>
        <p className="text-gray-700 mb-4">
          Testez gratuitement et partagez votre expérience. Votre feedback façonne l'avenir de
          Phoenix.
        </p>
        <a
          href="#"
          className="btn-secondary bg-purple-700 text-white hover:bg-purple-800 font-bold py-3 px-8 rounded-full text-lg transition duration-300 ease-in-out shadow-lg"
        >
          Donner mon Feedback
        </a>
      </div>
      {customHtml ? (
        <div className="mt-8 max-w-3xl mx-auto">
          <RenderHtml html={customHtml} />
        </div>
      ) : null}
    </section>
  );
};

export default AuthenticTestimonialsSection;

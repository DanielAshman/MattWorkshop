import { useState } from 'react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function ProductCard({ item, onAdded, isFavourite, onToggleFavourite }) {
  const { refreshBasket } = useAuth();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);

  async function handleAdd() {
    setLoading(true);
    setMessage('');
    try {
      await api.addToBasket(item.id);
      await refreshBasket();
      setIsError(false);
      setMessage('Added!');
      onAdded?.();
    } catch (error) {
      setIsError(true);
      setMessage(error.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleToggleFavourite() {
    setMessage('');
    try {
      await onToggleFavourite(item);
    } catch (error) {
      setIsError(true);
      setMessage(error.message);
    }
  }

  return (
    <article className="card flex flex-col overflow-hidden p-0 transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="relative aspect-square overflow-hidden bg-slate-100">
        <img
          src={item.picture_uri}
          alt={item.name}
          className="h-full w-full object-cover"
        />
        {onToggleFavourite && (
          <button
            type="button"
            onClick={handleToggleFavourite}
            aria-pressed={Boolean(isFavourite)}
            aria-label={isFavourite ? 'Remove from favourites' : 'Add to favourites'}
            className="absolute right-3 top-3 flex h-10 w-10 items-center justify-center rounded-full bg-white/90 text-xl shadow hover:bg-white"
          >
            <span className={isFavourite ? 'text-rose-500' : 'text-slate-400'}>
              {isFavourite ? '♥' : '♡'}
            </span>
          </button>
        )}
      </div>
      <div className="flex flex-1 flex-col gap-3 p-4">
        <div className="flex-1">
          <p className="text-xs font-medium uppercase tracking-wide text-indigo-600">
            {item.brand_name} · {item.type_name}
          </p>
          <h3 className="mt-1 text-lg font-semibold text-slate-900">{item.name}</h3>
          <p className="mt-2 text-sm text-slate-500 line-clamp-2">{item.description}</p>
        </div>
        <div className="flex items-center justify-between gap-3">
          <p className="text-xl font-bold text-slate-900">${item.price.toFixed(2)}</p>
          <button
            type="button"
            onClick={handleAdd}
            disabled={loading}
            className="btn-primary"
          >
            {loading ? 'Adding...' : 'Add to basket'}
          </button>
        </div>
        {message && (
          <p className={`text-xs font-medium ${isError ? 'text-red-600' : 'text-emerald-600'}`}>
            {message}
          </p>
        )}
      </div>
    </article>
  );
}

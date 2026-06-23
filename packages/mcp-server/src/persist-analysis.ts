import { getTickerBySymbol, saveAnalysisSnapshot } from '@stock-buddy/db';

const MCP_VERSION = '2.0.0';

/** Persist analyze_ticker output when STOCK_BUDDY_PERSIST_ANALYSIS=1 and DATABASE_URL is set. */
export async function maybePersistAnalysis(
  result: Record<string, unknown>,
  clientId?: string,
): Promise<number | undefined> {
  if (process.env.STOCK_BUDDY_PERSIST_ANALYSIS !== '1') return undefined;
  if (!process.env.DATABASE_URL) return undefined;
  if (result.skill !== 'analyze_ticker') return undefined;

  const tickerSymbol = String(result.ticker ?? '');
  if (!tickerSymbol) return undefined;

  const { createDb, closeDb } = await import('@stock-buddy/db');
  const db = createDb();
  try {
    const ticker = await getTickerBySymbol(db, tickerSymbol);
    if (!ticker) return undefined;

    const row = await saveAnalysisSnapshot(db, {
      tickerId: ticker.id,
      skill: 'analyze_ticker',
      asOf: String(result.as_of ?? new Date().toISOString().slice(0, 10)),
      payload: result,
      clientId,
      modelVersion: MCP_VERSION,
    });
    return row.id;
  } finally {
    await closeDb(db);
  }
}

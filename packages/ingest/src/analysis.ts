import {
  getTickerBySymbol,
  recordIngestRun,
  saveAnalysisSnapshot,
  updateFreshness,
  type Db,
} from '@stock-buddy/db';
import { analyzeTicker } from '@stock-buddy/mcp-server/composites';
import { buildTickerContract, stripMeta } from './contract-builder.js';

const MCP_VERSION = '2.0.0';

export interface RunAnalysisOptions {
  includePortfolio?: boolean;
  ohlcvDays?: number;
  clientId?: string;
  persist?: boolean;
}

/** Build contract from DB, run analyze_ticker pipeline, optionally persist snapshot. */
export async function runTickerAnalysis(
  db: Db,
  symbol: string,
  opts: RunAnalysisOptions = {},
): Promise<{
  analysis: Record<string, unknown>;
  snapshotId?: number;
}> {
  const contract = await buildTickerContract(db, symbol, {
    includePortfolio: opts.includePortfolio ?? true,
    ohlcvDays: opts.ohlcvDays ?? 260,
  });
  const analysis = analyzeTicker(stripMeta(contract));

  let snapshotId: number | undefined;
  if (opts.persist ?? true) {
    const ticker = await getTickerBySymbol(db, symbol);
    if (ticker) {
      const row = await saveAnalysisSnapshot(db, {
        tickerId: ticker.id,
        skill: 'analyze_ticker',
        asOf: String(analysis.as_of ?? contract.as_of),
        payload: analysis,
        clientId: opts.clientId,
        modelVersion: MCP_VERSION,
      });
      snapshotId = row.id;
    }
  }

  return { analysis, snapshotId };
}

export async function ingestAnalysis(db: Db, symbol: string): Promise<number> {
  const started = new Date();
  const ticker = await getTickerBySymbol(db, symbol);
  if (!ticker) {
    throw new Error(`Ticker not found: ${symbol}`);
  }

  try {
    const { snapshotId } = await runTickerAnalysis(db, symbol, { persist: true });
    await recordIngestRun(db, {
      jobName: 'ingest_analysis',
      tickerId: ticker.id,
      status: 'ok',
      rowsUpserted: 1,
      source: 'skills',
      startedAt: started,
    });
    await updateFreshness(db, 'analysis', ticker.id, true, 24);
    return snapshotId ?? 0;
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    await recordIngestRun(db, {
      jobName: 'ingest_analysis',
      tickerId: ticker.id,
      status: 'failed',
      errorMessage: message,
      startedAt: started,
    });
    await updateFreshness(db, 'analysis', ticker.id, false, 24);
    throw err;
  }
}

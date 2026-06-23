import { describe, expect, it } from 'vitest';
import {
  closeDb,
  createDb,
  getLatestAnalysisSnapshot,
  getTickerBySymbol,
  saveAnalysisSnapshot,
} from '@stock-buddy/db';
import { analyzeTicker } from '../packages/mcp-server/src/composites.ts';
import { buildTickerContract, stripMeta } from '@stock-buddy/ingest';
import { runTickerAnalysis } from '@stock-buddy/ingest';

const dbUrl = process.env.DATABASE_URL;
const describeDb = dbUrl ? describe : describe.skip;

describeDb('analysis snapshot persistence', () => {
  it('saveAnalysisSnapshot stores and retrieves analyze_ticker payload', async () => {
    const db = createDb(dbUrl);
    try {
      const ticker = await getTickerBySymbol(db, 'UPGDCL');
      expect(ticker).toBeTruthy();

      const payload = analyzeTicker({ ticker: 'UPGDCL', as_of: '2026-06-23' });
      const row = await saveAnalysisSnapshot(db, {
        tickerId: ticker!.id,
        skill: 'analyze_ticker',
        asOf: '2026-06-23',
        payload,
        clientId: 'test',
        modelVersion: '2.0.0',
      });

      expect(row.id).toBeGreaterThan(0);

      const latest = await getLatestAnalysisSnapshot(db, ticker!.id);
      expect(latest?.payload.skill).toBe('analyze_ticker');
      expect(latest?.clientId).toBe('test');
    } finally {
      await closeDb(db);
    }
  });

  it('runTickerAnalysis persists when ticker has market data', async () => {
    const db = createDb(dbUrl);
    try {
      const ticker = await getTickerBySymbol(db, 'UPGDCL');
      expect(ticker).toBeTruthy();

      const contract = await buildTickerContract(db, 'UPGDCL', { includePortfolio: true });
      if ((contract.ohlcv as unknown[]).length < 30) {
        return; // skip if no data in CI
      }

      const { analysis, snapshotId } = await runTickerAnalysis(db, 'UPGDCL', {
        clientId: 'vitest',
        persist: true,
      });
      expect(analysis.skill).toBe('analyze_ticker');
      expect(snapshotId).toBeGreaterThan(0);

      const latest = await getLatestAnalysisSnapshot(db, ticker!.id);
      expect(latest?.id).toBe(snapshotId);
    } finally {
      await closeDb(db);
    }
  });
});

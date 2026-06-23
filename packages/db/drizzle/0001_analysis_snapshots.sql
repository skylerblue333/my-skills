CREATE TABLE "analysis_snapshots" (
	"id" serial PRIMARY KEY NOT NULL,
	"ticker_id" integer NOT NULL,
	"skill" text DEFAULT 'analyze_ticker' NOT NULL,
	"as_of" date NOT NULL,
	"payload" jsonb NOT NULL,
	"client_id" text,
	"model_version" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "analysis_snapshots" ADD CONSTRAINT "analysis_snapshots_ticker_id_tickers_id_fk" FOREIGN KEY ("ticker_id") REFERENCES "public"."tickers"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "analysis_snapshots_ticker_created_idx" ON "analysis_snapshots" USING btree ("ticker_id","created_at");--> statement-breakpoint
CREATE INDEX "analysis_snapshots_skill_idx" ON "analysis_snapshots" USING btree ("skill");

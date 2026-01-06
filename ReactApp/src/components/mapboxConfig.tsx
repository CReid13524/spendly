import { FilterSpecification, GeoJSONSourceSpecification } from "mapbox-gl";

export const TRANSACTION_POINT_SOURCE_ID = "transaction-point-source"
export const TRANSACTION_POINT_LAYER_ID = "transaction-point-layer"
export const TRANSACTION_POINT_CLUSTER_CIRCLE_LAYER_ID = "transaction-point-cluster-circle-layer"
export const TRANSACTION_POINT_CLUSTER_TEXT_LAYER_ID = "transaction-point-cluster-text-layer"
export const TRANSACTION_POINT_DOT_LAYER_ID = "transaction-point-dot-layer"

export const TRANSACTION_POINT_BASE_FILTER: FilterSpecification = ['!', ['has', 'point_count']]
export const TRANSACTION_POINT_CLUSTER_BASE_FILTER: FilterSpecification = ['has', 'point_count']

export const TRANSACTION_POINT_SOURCE_SETTINGS: GeoJSONSourceSpecification = {
    type: "geojson",
    cluster: true,
    clusterRadius: 15,
    clusterMaxZoom: 14,
}

export const DEFAULT_DATA: GeoJSON.FeatureCollection = {type: "FeatureCollection", features: []}

export function createTransactionMarker(
  color: string,
  active: boolean = false
): HTMLCanvasElement {
  const width = 64;
  const height = 72;

  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;

  const ctx = canvas.getContext("2d")!;
  const cx = width / 2;

  const headY = 26;
  const headRadius = 20;
  const tipY = 62;

  /* ---------------- Shadow ---------------- */
  ctx.beginPath();
  ctx.ellipse(cx, tipY + 3, 9, 3, 0, 0, Math.PI * 2);
  ctx.fillStyle = "rgba(0,0,0,0.25)";
  ctx.fill();

  /* ================= OUTER (WHITE) ================= */
  ctx.beginPath();

  // Top half circle
  ctx.arc(cx, headY, headRadius, Math.PI, 0, false);

  // Right side to tip (tight curve)
  ctx.bezierCurveTo(
    cx + headRadius,
    headY + 10,
    cx + 6,
    headY + 30,
    cx,
    tipY
  );

  // Left side back up
  ctx.bezierCurveTo(
    cx - 6,
    headY + 30,
    cx - headRadius,
    headY + 10,
    cx - headRadius,
    headY
  );

  ctx.closePath();
  ctx.fillStyle = "#ffffff";
  ctx.fill();

  /* ================= INNER (COLOUR) ================= */
  ctx.beginPath();

  const innerRadius = 16;
  const inset = 4;

  ctx.arc(cx, headY, innerRadius, Math.PI, 0, false);

  ctx.bezierCurveTo(
    cx + innerRadius,
    headY + 8,
    cx + 4,
    headY + 26,
    cx,
    tipY - inset
  );

  ctx.bezierCurveTo(
    cx - 4,
    headY + 26,
    cx - innerRadius,
    headY + 8,
    cx - innerRadius,
    headY
  );

  ctx.closePath();
  ctx.fillStyle = color;
  ctx.fill();

  /* ---------------- Active "X" badge ---------------- */
  if (active) {
      const badgeRadius = 10;
      const badgeX = cx + headRadius - badgeRadius;
      const badgeY = 28 - headRadius + badgeRadius;

      // Circle background
      ctx.beginPath();
      ctx.arc(badgeX, badgeY, badgeRadius, 0, Math.PI * 2);
      ctx.fillStyle = "#000";
      ctx.fill();

      // X
      ctx.strokeStyle = "#fff";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(badgeX - 4, badgeY - 4);
      ctx.lineTo(badgeX + 4, badgeY + 4);
      ctx.moveTo(badgeX + 4, badgeY - 4);
      ctx.lineTo(badgeX - 4, badgeY + 4);
      ctx.stroke();
  }

  return canvas;
}



export function createNewTransactionMarker(): HTMLCanvasElement {
  const width = 64;
  const height = 80;

  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;

  const ctx = canvas.getContext("2d")!;
  const cx = width / 2;

  const tipY = height - 2;       // ✅ anchor point
  const topCenterY = 28;         // visual center
  const topRadius = 22;

  /* ---------------- Shadow (below tip) ---------------- */
  ctx.beginPath();
  ctx.ellipse(cx, tipY + 3, 10, 4, 0, 0, Math.PI * 2);
  ctx.fillStyle = "rgba(0,0,0,0.25)";
  ctx.fill();

  /* ---------------- Pin body ---------------- */
  ctx.beginPath();

  // Top half circle
  ctx.arc(cx, topCenterY, topRadius, Math.PI, 0, false);

  // Right curve to tip
  ctx.bezierCurveTo(
    cx + topRadius,
    topCenterY + 14,
    cx + 10,
    tipY - 14,
    cx,
    tipY
  );

  // Left curve back up
  ctx.bezierCurveTo(
    cx - 10,
    tipY - 14,
    cx - topRadius,
    topCenterY + 14,
    cx - topRadius,
    topCenterY
  );

  ctx.closePath();
  ctx.fillStyle = '#FE2C55';
  ctx.fill();

  /* ---------------- Inner white badge ---------------- */
  ctx.beginPath();
  ctx.arc(cx, topCenterY, 16, 0, Math.PI * 2);
  ctx.fillStyle = "#fff";
  ctx.fill();


  /* ---------------- Amount text ---------------- */
  ctx.fillStyle = "#111";
  ctx.font = "600 8px Inter, system-ui, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  ctx.fillText('Drag', cx, 28);

  return canvas;
}


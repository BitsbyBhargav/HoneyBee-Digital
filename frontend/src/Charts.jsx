import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  LabelList,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { MapPin, Shapes, Database } from "lucide-react";
import { number } from "./api";

const colors = [
  "#e8b43e",
  "#7d8f75",
  "#7e9eae",
  "#b6a3b9",
  "#bd9273",
  "#86a9a4",
  "#c6cbd2",
];

function PanelHeading({ icon: Icon, title, subtitle, badge }) {
  return (
    <div className="panel-heading">
      <div>
        <h2>
          <Icon size={17} />
          {title}
        </h2>
        <p>{subtitle}</p>
      </div>
      <span className="badge">{badge}</span>
    </div>
  );
}

function AccessibleCounts({ items, label }) {
  return (
    <details className="chart-values">
      <summary>View {label} values</summary>
      <ul>
        {items.map((item) => (
          <li key={item.name}>
            {item.name}: {number(item.count)}
          </li>
        ))}
      </ul>
    </details>
  );
}

export default function Charts({ cities, categories, sources }) {
  const top = categories.items.slice(0, 6);
  if (categories.items.length > 6)
    top.push({
      name: "Other categories",
      count: categories.items
        .slice(6)
        .reduce((sum, item) => sum + item.count, 0),
    });
  return (
    <div className="charts-grid">
      <section
        className="panel city-panel"
        aria-label="City-wise business counts"
      >
        <PanelHeading
          icon={MapPin}
          title="Business by city"
          subtitle="Distribution across collection areas"
          badge={`${cities.items.length} cities`}
        />
        <div className="city-chart">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={cities.items}
              margin={{ top: 24, right: 18, bottom: 0, left: -16 }}
            >
              <CartesianGrid
                strokeDasharray="3 4"
                vertical={false}
                stroke="#edf0f3"
              />
              <XAxis
                dataKey="name"
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#637082", fontSize: 12 }}
                dy={9}
                interval={0}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                allowDecimals={false}
                tick={{ fill: "#8a94a3", fontSize: 11 }}
              />
              <Tooltip
                cursor={{ fill: "#fbf6e9" }}
                formatter={(value) => [number(value), "Businesses"]}
                contentStyle={{ border: "1px solid #e8ebef", borderRadius: 10 }}
              />
              <Bar
                dataKey="count"
                fill="#e8b43e"
                radius={[5, 5, 0, 0]}
                maxBarSize={62}
                isAnimationActive={false}
              >
                <LabelList
                  dataKey="count"
                  position="top"
                  formatter={number}
                  fill="#4b5563"
                  fontSize={12}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <AccessibleCounts items={cities.items} label="city" />
      </section>
      <section
        className="panel category-panel"
        id="categories"
        aria-label="Category-wise business counts"
      >
        <PanelHeading
          icon={Shapes}
          title="Business by category"
          subtitle="Six largest categories, plus all others"
          badge={`${categories.items.length} total`}
        />
        <div className="category-chart">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={top}
              layout="vertical"
              margin={{ left: 0, right: 45, top: 6, bottom: 2 }}
            >
              <XAxis type="number" hide />
              <YAxis
                type="category"
                dataKey="name"
                width={112}
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#637082", fontSize: 12 }}
              />
              <Tooltip
                cursor={{ fill: "#f7f8fa" }}
                formatter={(value) => [number(value), "Businesses"]}
                contentStyle={{ border: "1px solid #e8ebef", borderRadius: 10 }}
              />
              <Bar
                dataKey="count"
                radius={[0, 4, 4, 0]}
                barSize={15}
                isAnimationActive={false}
              >
                {top.map((item, index) => (
                  <Cell key={item.name} fill={colors[index]} />
                ))}
                <LabelList
                  dataKey="count"
                  position="right"
                  formatter={number}
                  fill="#4b5563"
                  fontSize={11}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <AccessibleCounts items={categories.items} label="category" />
      </section>
      <section
        className="panel source-panel"
        aria-label="Source-wise business counts"
      >
        <PanelHeading
          icon={Database}
          title="Data sources"
          subtitle="Where these listings come from"
          badge={`${sources.items.length} source${sources.items.length === 1 ? "" : "s"}`}
        />
        <div className="source-body">
          <div className="donut-wrap">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={sources.items}
                  dataKey="count"
                  nameKey="name"
                  innerRadius="70%"
                  outerRadius="90%"
                  paddingAngle={sources.items.length > 1 ? 3 : 0}
                  stroke="none"
                  isAnimationActive={false}
                >
                  {sources.items.map((item, index) => (
                    <Cell
                      key={item.name}
                      fill={colors[index % colors.length]}
                    />
                  ))}
                </Pie>
                <Tooltip formatter={number} />
              </PieChart>
            </ResponsiveContainer>
            <div className="donut-label">
              <strong>{number(sources.total)}</strong>
              <span>total listings</span>
            </div>
          </div>
          <div className="source-legend">
            {sources.items.map((item, index) => (
              <div key={item.name}>
                <span
                  className="legend-dot"
                  style={{ background: colors[index % colors.length] }}
                />
                <span>{item.name}</span>
                <strong>{number(item.count)}</strong>
                <small>
                  {((item.count / sources.total) * 100).toFixed(0)}%
                </small>
              </div>
            ))}
          </div>
        </div>
        <p className="source-note">
          Collected through a structured API. Source links are available in the
          directory below.
        </p>
      </section>
    </div>
  );
}

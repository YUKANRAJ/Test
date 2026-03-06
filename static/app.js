let products = [];
let bill = [];

function rs(v) { return Number(v || 0).toFixed(2); }

async function api(url, options = {}) {
  const res = await fetch(url, { headers: { "Content-Type": "application/json" }, ...options });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Request failed");
  return data;
}

function renderProductTable() {
  const table = document.getElementById("productTable");
  table.innerHTML = products.map(p => `
    <tr>
      <td>${p.name}</td>
      <td>${p.unit_type}</td>
      <td>₹${rs(p.price)}</td>
      <td>${p.barcode || "-"}</td>
      <td>
        <button onclick='editProduct(${JSON.stringify(p)})'>Edit</button>
        <button class='danger' onclick='deleteProduct(${p.id})'>Delete</button>
      </td>
    </tr>
  `).join("");

  const select = document.getElementById("billProduct");
  select.innerHTML = products.map(p => `<option value="${p.id}">${p.name} (₹${rs(p.price)}/${p.unit_type})</option>`).join("");
}

function editProduct(p) {
  document.getElementById("productId").value = p.id;
  document.getElementById("productName").value = p.name;
  document.getElementById("unitType").value = p.unit_type;
  document.getElementById("productPrice").value = p.price;
  document.getElementById("productBarcode").value = p.barcode || "";
}

function resetProductForm() {
  document.getElementById("productForm").reset();
  document.getElementById("productId").value = "";
}

async function loadProducts() {
  const search = document.getElementById("searchInput").value.trim();
  const barcode = document.getElementById("barcodeInput").value.trim();
  const query = new URLSearchParams();
  if (search) query.set("search", search);
  if (barcode) query.set("barcode", barcode);
  products = await api(`/api/products?${query.toString()}`);
  renderProductTable();
}

async function deleteProduct(id) {
  if (!confirm("Delete this product?")) return;
  await api(`/api/products/${id}`, { method: "DELETE" });
  await loadProducts();
}

document.getElementById("productForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("productId").value;
  const payload = {
    name: document.getElementById("productName").value,
    unit_type: document.getElementById("unitType").value,
    price: document.getElementById("productPrice").value,
    barcode: document.getElementById("productBarcode").value,
  };

  if (id) {
    await api(`/api/products/${id}`, { method: "PUT", body: JSON.stringify(payload) });
  } else {
    await api("/api/products", { method: "POST", body: JSON.stringify(payload) });
  }
  resetProductForm();
  await loadProducts();
});

function addToBill() {
  const productId = Number(document.getElementById("billProduct").value);
  const qty = Number(document.getElementById("billQty").value);
  if (!productId || qty <= 0) return;

  const p = products.find(x => x.id === productId);
  const subtotal = p.price * qty;
  bill.push({ product_id: p.id, product_name: p.name, unit_type: p.unit_type, quantity: qty, unit_price: p.price, subtotal });
  document.getElementById("billQty").value = "";
  refreshBill();
}

function removeBillItem(index) {
  bill.splice(index, 1);
  refreshBill();
}

function refreshBill() {
  const tbody = document.getElementById("billItems");
  tbody.innerHTML = bill.map((i, idx) => `
    <tr>
      <td>${i.product_name}</td>
      <td>${i.quantity} ${i.unit_type}</td>
      <td>₹${rs(i.unit_price)}</td>
      <td>₹${rs(i.subtotal)}</td>
      <td><button class='danger' onclick='removeBillItem(${idx})'>x</button></td>
    </tr>
  `).join("");

  const subtotal = bill.reduce((sum, i) => sum + i.subtotal, 0);
  const taxPercent = Number(document.getElementById("taxPercent").value || 0);
  const tax = subtotal * taxPercent / 100;
  const total = subtotal + tax;
  document.getElementById("subtotal").textContent = rs(subtotal);
  document.getElementById("tax").textContent = rs(tax);
  document.getElementById("total").textContent = rs(total);
}

async function saveBill() {
  if (!bill.length) return alert("Add items to bill first");
  const taxPercent = Number(document.getElementById("taxPercent").value || 0);
  const payload = { items: bill.map(i => ({ product_id: i.product_id, quantity: i.quantity })), tax_percent: taxPercent };
  const data = await api("/api/sales", { method: "POST", body: JSON.stringify(payload) });
  document.getElementById("billMessage").textContent = `Bill #${data.sale_id} saved. Total ₹${rs(data.total)}`;
  bill = [];
  refreshBill();
  loadHistory();
  loadDailyReport();
}

async function loadHistory() {
  const rows = await api("/api/sales/history");
  document.getElementById("historyTable").innerHTML = rows.map(r => `
    <tr>
      <td>${r.id}</td>
      <td>${r.created_at.replace("T", " ")}</td>
      <td>₹${rs(r.subtotal)}</td>
      <td>₹${rs(r.tax_amount)}</td>
      <td>₹${rs(r.total)}</td>
    </tr>
  `).join("");
}

async function loadDailyReport() {
  const rows = await api("/api/sales/report/daily");
  document.getElementById("dailyTable").innerHTML = rows.map(r => `
    <tr><td>${r.sale_date}</td><td>${r.bills}</td><td>₹${rs(r.total_sales)}</td></tr>
  `).join("");
}

(async function init() {
  await loadProducts();
  await loadHistory();
  await loadDailyReport();
})();

> # 🍴 Maaty Fork — Packaging + Service Layer
>
> Bu repo, [`ZekaiSuni/claude-for-legal-turkish`](https://github.com/ZekaiSuni/claude-for-legal-turkish) deposunun **Maaty** (https://maaty.net) tarafından maintain edilen bir fork'udur. **Skill içeriği (markdown manifest'leri, instructions, çıktı örnekleri) DEĞİŞTİRİLMEZ** — Maaty'nin eklediği yalnızca paketleme ve servis altyapısıdır.
>
> **Maaty'nin amacı:** Bu plugin'leri Maaty production stack'inde HTTP servis (FastAPI) olarak çalıştırmak. `legal_plugins/` dizininde (Faz 6.1+'da eklenecek) skill manifest'lerini yükleyen + Maaty BYOK akışı (Gemini/OpenAI/Anthropic) ile çalışan bir servis bulunur. Kullanıcılar Maaty UI'dan ("Hukuk Skill Kütüphanesi" bölümü) skill'leri çağırır.
>
> **Upstream zinciri:**
> - **Direct upstream:** [ZekaiSuni/claude-for-legal-turkish](https://github.com/ZekaiSuni/claude-for-legal-turkish) — Türk hukuku adaptasyon işinin tamamı (TBK, TTK, KVKK, HMK, İK kavramları, 145+ skill TR uyarlaması)
> - **Original upstream:** [anthropics/claude-for-legal](https://github.com/anthropics/claude-for-legal) — Plugin/skill mimarisinin orijinali
>
> Tüm orijinal copyright + attribution korunur (Apache 2.0). Detay için bkz. [`NOTICE`](./NOTICE).

---

# Claude Legal Turkish

Claude Legal Turkish, Anthropic'in açık kaynaklı **Claude for Legal** yapısını temel alan Türkiye uyarlamasıdır. Amaç, aynı plugin/skill iskeletini koruyarak hukuki içerikleri Türk hukuku, Türkiye yargı sistemi ve yerel regülasyonlar ekseninde çalışır hale getirmektir.

Bu repo; hukuk departmanları, avukatlar, uyum ekipleri ve hukuk operasyonları için sözleşme inceleme, dava/uyuşmazlık takibi, KVKK, iş hukuku, ürün hukuku, şirketler hukuku ve regülasyon izleme iş akışlarına yönelik Claude Code plugin'leri içerir.

> Önemli: Bu proje hukuki danışmanlık vermez. Üretilen her çıktı avukat/hukukçu incelemesine tabi taslak, araştırma notu veya karar destek çıktısıdır. Kanun, içtihat, süre, tebliğ, yetki, imza ve resmi kaynak kontrolleri somut dosya için ayrıca doğrulanmalıdır.

## Tasarım Kararı

Operasyonel adlar orijinal repo ile uyumlu tutulur:

- Plugin klasörleri: `commercial-legal`, `litigation-legal`, `privacy-legal` vb.
- Komutlar: `/commercial-legal:review`, `/regulatory-legal:reg-feed-watcher` vb.
- Dosya adları: `SKILL.md`, `CLAUDE.md`, `.mcp.json`, `.claude-plugin/plugin.json`

Türkçeleştirme; hukuki içerikte, kontrol listelerinde, çıktı şablonlarında, örneklerde ve kaynak/kavram katmanında yapılır. Komut adlarını `/ticari-hukuk:*` gibi Türkçeleştirmek ayrı bir repo-geneli refactor işidir.

## Durum Özeti

| Alan | Durum | Not |
|---|---|---|
| `commercial-legal` | Uyarlandı | Türk ticari sözleşme pratiğine göre uyarlandı. |
| `corporate-legal` | Uyarlandı | Türk şirketler hukuku pratiğine göre uyarlandı. |
| `litigation-legal` | Uyarlandı | Türkiye yargı ve dava pratiğine göre uyarlandı. |
| `privacy-legal` | Uyarlandı | KVKK pratiğine göre uyarlandı. |
| `employment-legal` | Uyarlandı | Türk iş hukuku pratiğine göre uyarlandı. |
| `product-legal` | Uyarlandı | Türk ürün, tüketici, reklam ve e-ticaret pratiğine göre uyarlandı. |
| `regulatory-legal` | Uyarlandı | Türkiye regülasyon izleme pratiğine göre uyarlandı. |
| `managed-agent-cookbooks` | Uyarlandı | Türkiye kaynak ve takip mantığına göre uyarlandı. |
| `ip-legal` | Uyarlandı | Türk fikri mülkiyet pratiğine göre uyarlandı. |
| `ai-governance-legal` | Uyarlandı | Türkiye AI yönetişimi ve KVKK odağıyla uyarlandı. |
| `legal-builder-hub` | Uyarlanmadı | Hukuki içerik modülü değil, teknik/meta araç olduğu için kapsam dışında bırakıldı. |
| `law-student` | Uyarlanmadı | ABD hukuk eğitimi/bar prep modeline dayandığı için kapsam dışında bırakıldı. |
| `legal-clinic` | Uyarlanmadı | US law school clinic modeline dayandığı için kapsam dışında bırakıldı. |
| `cocounsel-legal` | Uyarlanmadı | Üçüncü taraf Westlaw/Practical Law plugin'i olduğu için değiştirilmedi. |

Ayrıntılı takip için: [TURKISH_ADAPTATION_STATUS.md](TURKISH_ADAPTATION_STATUS.md)

## Kurulum

Claude Code içinde bu klasörü yerel marketplace olarak ekleyin:

```text
/plugin marketplace add C:\path\to\legal-turkish-master
```

Bir plugin kurun:

```text
/plugin install commercial-legal@legal-turkish
```

Claude Code'u yeniden başlatın. Ardından ilgili plugin'in başlangıç mülakatını çalıştırın:

```text
/commercial-legal:cold-start-interview
```

İlk kullanım örneği:

```text
/commercial-legal:review "C:\sozlesmeler\tedarikci-taslak.docx"
```

Diğer örnekler:

```text
/litigation-legal:demand-intake
/privacy-legal:pia-generation
/employment-legal:termination-review
/regulatory-legal:reg-feed-watcher
```

Kısa kurulum akışı için: [QUICKSTART.md](QUICKSTART.md)

## Bağlantılar ve MCP

Plugin'lerde Slack, Google Drive, Box, Linear, Asana gibi operasyonel bağlayıcılar opsiyonel olarak korunmuştur. Türk hukuk kaynaklarına yönelik yerel araştırma omurgası için `.mcp.json` dosyalarında **Yargı MCP** önerilir.

Yargı MCP; Yargıtay, Danıştay, Anayasa Mahkemesi, KVKK, Rekabet Kurumu ve benzeri Türkiye kaynaklarına erişim için kullanılır. Bağlantı çalışmıyorsa veya bağlı değilse çıktılardaki kaynak/citation etiketleri doğrulama uyarısı taşır.

## Repo Yapısı

```text
legal-turkish-master/
├── .claude-plugin/
│   └── marketplace.json
├── commercial-legal/
├── corporate-legal/
├── litigation-legal/
├── privacy-legal/
├── employment-legal/
├── product-legal/
├── regulatory-legal/
├── ip-legal/
├── ai-governance-legal/
├── managed-agent-cookbooks/
├── legal-builder-hub/
├── references/
└── scripts/
```

## Doğrulama

Bu çalışma kopyasında yapılan son yapısal kontroller:

- Marketplace `source` yolları ve plugin manifestleri çözümleniyor.
- Tüm JSON dosyaları parse ediliyor.
- Somut plugin komut atıfları mevcut skill klasörlerine gidiyor.
- Managed-agent `manifest`, `file` ve `from_plugin` referansları çözümleniyor.
- Ana `claude-for-legal-main` iskeletine göre eksik dosya yok.
- Operasyonel identifier kontrolleri yapıldı (`reg-feed-watcher`, `feed-reader` korunur).

Windows ortamında `bash` ve `pyyaml` yoksa repo'nun `scripts/test-cookbooks.sh` harness'i birebir çalışmayabilir; bu durumda eşdeğer statik kontroller PowerShell/Node ile yapılabilir.

## Yayın Notu

Bu repo bir Türkiye uyarlama çalışmasıdır. Orijinal Claude for Legal projesinin lisans ve katkı koşulları korunur. Uyarlanan içeriklerde Türk hukuku terminolojisi kullanılsa da hiçbir çıktı doğrudan hukuki mütalaa, avukat görüşü veya resmi kaynak doğrulaması yerine geçmez.

## Lisans

Apache License 2.0. Ayrıntı için [LICENSE](LICENSE).

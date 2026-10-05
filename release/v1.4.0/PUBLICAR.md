# Publicar a release v1.4.0

Os artefatos já ficam prontos nesta pasta após rodar `scripts/release.sh`:

```
release/v1.4.0/
├── CofreDeSenhas-1.4-x86_64.AppImage
├── SHA256SUMS
├── SHA256SUMS.asc
├── DANIEL-PUBKEY.asc
└── RELEASE_NOTES.md
```

Antes de publicar, confira que o commit/tag aponta para o código da versão.

---

## Opção A — `gh` CLI (recomendado)

```bash
gh release create v1.4.0 \
  release/v1.4.0/CofreDeSenhas-1.4-x86_64.AppImage \
  release/v1.4.0/SHA256SUMS \
  release/v1.4.0/SHA256SUMS.asc \
  release/v1.4.0/DANIEL-PUBKEY.asc \
  --title "CofreDeSenhas 1.4" \
  --notes-file release/v1.4.0/RELEASE_NOTES.md \
  --prerelease
```

## Opção B — tag no Git + interface do GitHub

```bash
git tag -a v1.4.0 -m "CofreDeSenhas 1.4"
git push origin v1.4.0
```

Depois, em **Releases → Draft a new release**:
1. Selecione a tag `v1.4.0`.
2. Título: `CofreDeSenhas 1.4`.
3. Cole o conteúdo de `RELEASE_NOTES.md` na descrição.
4. Marque **Set as a pre-release**.
5. Anexe os 4 arquivos (`AppImage`, `SHA256SUMS`, `SHA256SUMS.asc`, `DANIEL-PUBKEY.asc`).
6. Publique.

## Opção C — API do GitHub (curl)

```bash
TAG=v1.4.0
TOKEN=SEU_TOKEN_COM_ESCOPO_REPO   # não commite este valor

# 1) Cria a release
curl -sS -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/danielexpe/cofre-senhas/releases \
  -d "{\"tag_name\":\"$TAG\",\"name\":\"CofreDeSenhas 1.4\",\"prerelease\":true,\"body\":$(python3 -c 'import json,sys;print(json.dumps(open("release/v1.4.0/RELEASE_NOTES.md").read()))')}"

# 2) Sobe cada artefato (use a URL upload_url retornada, sem "{?name,label}")
UPLOAD="https://uploads.github.com/repos/danielexpe/cofre-senhas/releases/<ID>/assets"
for f in CofreDeSenhas-1.4-x86_64.AppImage SHA256SUMS SHA256SUMS.asc DANIEL-PUBKEY.asc; do
  curl -sS -X POST \
    -H "Authorization: token $TOKEN" \
    -H "Content-Type: application/octet-stream" \
    --data-binary @"release/v1.4.0/$f" \
    "$UPLOAD?name=$f"
done
```

> Dica: para criar a tag junto com a release via API, adicione
> `"target_commitish":"main"` ao JSON do passo 1 (a tag é criada
> automaticamente se ainda não existir).

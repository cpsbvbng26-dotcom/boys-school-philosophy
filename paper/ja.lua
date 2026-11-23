-- Line breaking for a short Japanese passage in LuaLaTeX without a Japanese TeX package.
-- ja_emit(s) prints s with a stretchable break opportunity after each CJK character, except before closing
-- punctuation and after opening brackets. The passage contains no character that TeX treats specially.
local NOBREAK_BEFORE = { ["、"]=true, ["。"]=true, ["」"]=true, ["』"]=true, ["）"]=true, ["・"]=true, ["："]=true }
local NOBREAK_AFTER = { ["「"]=true, ["『"]=true, ["（"]=true }
local function cjk(c) return (c >= 0x3000 and c <= 0x9FFF) or (c >= 0xFF00 and c <= 0xFFEF) end
function ja_emit(s)
  local cs = {}
  for _, c in utf8.codes(s) do cs[#cs + 1] = c end
  local out = {}
  for i, c in ipairs(cs) do
    local ch = utf8.char(c)
    out[#out + 1] = ch
    local nx = cs[i + 1] and utf8.char(cs[i + 1])
    if cjk(c) and nx and not NOBREAK_BEFORE[nx] and not NOBREAK_AFTER[ch] then out[#out + 1] = "\\hskip0pt plus 0.5pt\\relax " end
  end
  tex.sprint(table.concat(out))
end

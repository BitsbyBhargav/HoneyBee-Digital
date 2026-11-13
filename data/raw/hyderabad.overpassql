[out:json][timeout:90];
(
 nwr["name"]["shop"]["shop"!~"^(vacant|no|closed|disused)$"]["addr:street"](17.28,78.3,17.55,78.62);
 nwr["name"]["amenity"~"^(restaurant|cafe|fast_food|pharmacy|bank|dentist|clinic|fuel|bar|pub|ice_cream)$"]["addr:street"](17.28,78.3,17.55,78.62);
 nwr["name"]["shop"]["shop"!~"^(vacant|no|closed|disused)$"]["addr:full"](17.28,78.3,17.55,78.62);
 nwr["name"]["amenity"~"^(restaurant|cafe|fast_food|pharmacy|bank|dentist|clinic|fuel|bar|pub|ice_cream)$"]["addr:full"](17.28,78.3,17.55,78.62);
);
out tags;

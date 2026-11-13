[out:json][timeout:90];
(
 nwr["name"]["shop"]["shop"!~"^(vacant|no|closed|disused)$"]["addr:street"](12.9,80.12,13.18,80.32);
 nwr["name"]["amenity"~"^(restaurant|cafe|fast_food|pharmacy|bank|dentist|clinic|fuel|bar|pub|ice_cream)$"]["addr:street"](12.9,80.12,13.18,80.32);
 nwr["name"]["shop"]["shop"!~"^(vacant|no|closed|disused)$"]["addr:full"](12.9,80.12,13.18,80.32);
 nwr["name"]["amenity"~"^(restaurant|cafe|fast_food|pharmacy|bank|dentist|clinic|fuel|bar|pub|ice_cream)$"]["addr:full"](12.9,80.12,13.18,80.32);
);
out tags;

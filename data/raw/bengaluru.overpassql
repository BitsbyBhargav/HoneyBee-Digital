[out:json][timeout:90];
(
 nwr["name"]["shop"]["shop"!~"^(vacant|no|closed|disused)$"]["addr:street"](12.85,77.48,13.08,77.74);
 nwr["name"]["amenity"~"^(restaurant|cafe|fast_food|pharmacy|bank|dentist|clinic|fuel|bar|pub|ice_cream)$"]["addr:street"](12.85,77.48,13.08,77.74);
 nwr["name"]["shop"]["shop"!~"^(vacant|no|closed|disused)$"]["addr:full"](12.85,77.48,13.08,77.74);
 nwr["name"]["amenity"~"^(restaurant|cafe|fast_food|pharmacy|bank|dentist|clinic|fuel|bar|pub|ice_cream)$"]["addr:full"](12.85,77.48,13.08,77.74);
);
out tags;

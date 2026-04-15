import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
	loader: glob({ base: './src/content/blog', pattern: '**/*.{md,mdx}' }),
	schema: z.object({
		title: z.string(),
		description: z.string().optional().default(''),
		// WordPress export uses 'date'; coerce handles both string and Date
		date: z.coerce.date(),
		updatedDate: z.coerce.date().optional(),
		categories: z.array(z.string()).optional().default([]),
		tags: z.array(z.string()).optional().default([]),
		coverImage: z.string().optional(),
		draft: z.boolean().optional().default(false),
	}),
});

export const collections = { blog };
